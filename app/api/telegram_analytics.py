"""
API для аналитики Telegram каналов
Специфичная аналитика для Telegram с метриками TGStat
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from models import SocialAccount, ProfileSnapshot, Video, Author
import statistics

router = APIRouter(prefix="/api/telegram-analytics", tags=["telegram-analytics"])


@router.get("/channel/{social_account_id}")
async def get_telegram_channel_analytics(
    social_account_id: int,
    current_start: datetime = Query(..., description="Начало текущего периода"),
    current_end: datetime = Query(..., description="Конец текущего периода"),
    previous_start: Optional[datetime] = Query(
        None, description="Начало прошлого периода для сравнения"
    ),
    previous_end: Optional[datetime] = Query(
        None, description="Конец прошлого периода для сравнения"
    ),
):
    """
    Получить полную аналитику по Telegram каналу

    Специфичные метрики для Telegram:
    - ERR% - процент вовлеченности подписчиков
    - ERR24% - процент вовлеченности подписчиков за первые 24 часа
    - ER% - коэффициент вовлеченности во взаимодействия
    - ИЦ (ci_index) - индекс цитирования
    - Средний охват поста
    - Рекламный охват (12h, 24h, 48h)
    - Дневной охват
    - Упоминания и пересылки
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    if social_account.platform != "telegram":
        raise HTTPException(
            status_code=400, detail="This endpoint only supports Telegram accounts"
        )

    # Вычисляем метрики для текущего периода
    current_metrics = await _calculate_telegram_period_metrics(
        social_account, current_start, current_end
    )

    # Вычисляем метрики для прошлого периода (если указан)
    previous_metrics = None
    comparison_metrics = None

    if previous_start and previous_end:
        previous_metrics = await _calculate_telegram_period_metrics(
            social_account, previous_start, previous_end
        )
        comparison_metrics = _calculate_comparison_metrics(
            current_metrics, previous_metrics
        )

    return {
        "social_account_id": social_account_id,
        "platform": social_account.platform,
        "current_period": {
            "start": current_start,
            "end": current_end,
            "metrics": current_metrics,
        },
        "previous_period": {
            "start": previous_start,
            "end": previous_end,
            "metrics": previous_metrics,
        }
        if previous_metrics
        else None,
        "comparison": comparison_metrics,
    }


@router.get("/authors/{author_id}")
async def get_author_telegram_analytics(
    author_id: int,
    current_start: datetime = Query(..., description="Начало текущего периода"),
    current_end: datetime = Query(..., description="Конец текущего периода"),
    previous_start: Optional[datetime] = Query(
        None, description="Начало прошлого периода для сравнения"
    ),
    previous_end: Optional[datetime] = Query(
        None, description="Конец прошлого периода для сравнения"
    ),
):
    """
    Получить аналитику по всем Telegram каналам автора

    Агрегирует данные со всех Telegram каналов автора
    """
    # Проверяем существование автора
    author = await Author.filter(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Получаем все Telegram аккаунты автора
    telegram_accounts = await SocialAccount.filter(
        author_id=author_id, platform="telegram", is_active=True
    ).all()

    if not telegram_accounts:
        raise HTTPException(
            status_code=404, detail="No active Telegram accounts found for this author"
        )

    # Собираем метрики по каждому каналу
    channels_data = []
    aggregated_current = {
        "F": 0,
        "F_prev": 0,
        "delta_F": 0,
        "P": 0,
        "V": 0,
        "E": 0,
        "total_reactions": 0,
        "total_comments": 0,
        "total_shares": 0,
        "avg_post_reach_sum": 0,
        "ci_index_sum": 0,
        "err_percent_sum": 0,
        "er_percent_sum": 0,
    }

    for account in telegram_accounts:
        current_metrics = await _calculate_telegram_period_metrics(
            account, current_start, current_end
        )

        channels_data.append(
            {
                "social_account_id": account.id,
                "username": account.username,
                "metrics": current_metrics,
            }
        )

        # Агрегируем метрики
        aggregated_current["F"] += current_metrics.get("F", 0)
        aggregated_current["F_prev"] += current_metrics.get("F_prev", 0)
        aggregated_current["delta_F"] += current_metrics.get("delta_F", 0)
        aggregated_current["P"] += current_metrics.get("P", 0)
        aggregated_current["V"] += current_metrics.get("V", 0)
        aggregated_current["E"] += current_metrics.get("E", 0)
        aggregated_current["total_reactions"] += current_metrics.get(
            "total_reactions", 0
        )
        aggregated_current["total_comments"] += current_metrics.get("total_comments", 0)
        aggregated_current["total_shares"] += current_metrics.get("total_shares", 0)
        aggregated_current["avg_post_reach_sum"] += current_metrics.get(
            "avg_post_reach", 0
        )
        aggregated_current["ci_index_sum"] += current_metrics.get("ci_index", 0)
        aggregated_current["err_percent_sum"] += current_metrics.get("err_percent", 0)
        aggregated_current["er_percent_sum"] += current_metrics.get("er_percent", 0)

    # Вычисляем средние значения
    num_channels = len(telegram_accounts)
    aggregated_current["delta_F_percent"] = (
        (aggregated_current["delta_F"] / max(aggregated_current["F_prev"], 1)) * 100
        if aggregated_current["F_prev"] > 0
        else 0
    )
    aggregated_current["V_avg"] = aggregated_current["V"] / max(
        aggregated_current["P"], 1
    )
    aggregated_current["E_avg"] = aggregated_current["E"] / max(
        aggregated_current["P"], 1
    )
    aggregated_current["ER_view"] = (
        (aggregated_current["E"] / max(aggregated_current["V"], 1)) * 100
        if aggregated_current["V"] > 0
        else 0
    )
    aggregated_current["avg_post_reach"] = aggregated_current[
        "avg_post_reach_sum"
    ] / max(num_channels, 1)
    aggregated_current["ci_index_avg"] = aggregated_current["ci_index_sum"] / max(
        num_channels, 1
    )
    aggregated_current["err_percent_avg"] = aggregated_current["err_percent_sum"] / max(
        num_channels, 1
    )
    aggregated_current["er_percent_avg"] = aggregated_current["er_percent_sum"] / max(
        num_channels, 1
    )

    return {
        "author_id": author_id,
        "author_name": author.name,
        "channels_count": num_channels,
        "period": {
            "start": current_start,
            "end": current_end,
        },
        "aggregated_metrics": aggregated_current,
        "channels": channels_data,
    }


async def _calculate_telegram_period_metrics(
    social_account: SocialAccount, period_start: datetime, period_end: datetime
) -> dict:
    """Вычислить все метрики за период для Telegram"""

    # Нормализуем даты
    period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
    period_end = period_end.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Получаем snapshot на конец периода
    end_snapshot = (
        await ProfileSnapshot.filter(
            social_account=social_account, snapshot_date__lte=period_end
        )
        .order_by("-snapshot_date")
        .first()
    )

    # Получаем snapshot на начало периода
    start_snapshot = (
        await ProfileSnapshot.filter(
            social_account=social_account, snapshot_date__lte=period_start
        )
        .order_by("-snapshot_date")
        .first()
    )

    # F - подписчики на конец периода
    F = end_snapshot.followers_count if end_snapshot else 0
    F_prev = start_snapshot.followers_count if start_snapshot else 0

    # ΔF - рост подписчиков
    delta_F = F - F_prev

    # ΔF% - рост подписчиков в процентах
    delta_F_percent = (delta_F / max(F_prev, 1)) * 100 if F_prev > 0 else 0

    # Получаем все посты за период
    posts = await Video.filter(
        social_account=social_account,
        created_at_platform__gte=period_start,
        created_at_platform__lte=period_end,
    ).all()

    # P - количество публикаций
    P = len(posts)

    # V - суммарные просмотры
    V = sum(p.views_count or 0 for p in posts)

    # В Telegram вовлечённость = реакции + комментарии + пересылки
    total_reactions = sum(
        p.likes_count or 0 for p in posts
    )  # likes_count хранит reactions
    total_comments = sum(p.comments_count or 0 for p in posts)
    total_shares = sum(p.shares_count or 0 for p in posts)

    # E - суммарная вовлечённость
    E = total_reactions + total_comments + total_shares

    # V_avg - средние просмотры на пост
    V_avg = V / max(P, 1) if P > 0 else 0

    # E_avg - средняя вовлечённость на пост
    E_avg = E / max(P, 1) if P > 0 else 0

    # ER_view - вовлечённость на просмотр (%)
    ER_view = (E / max(V, 1)) * 100 if V > 0 else 0

    # ERR% - процент вовлеченности подписчиков (просмотры / подписчики)
    ERR_percent = (V_avg / max(F, 1)) * 100 if F > 0 and P > 0 else 0

    # ER% - коэффициент вовлеченности (взаимодействия / подписчики)
    ER_percent = (E_avg / max(F, 1)) * 100 if F > 0 and P > 0 else 0

    # Медиана просмотров
    views_list = [p.views_count or 0 for p in posts if p.views_count]
    V_median = statistics.median(views_list) if views_list else 0

    # Медиана вовлечённости
    engagement_list = [
        (p.likes_count or 0) + (p.comments_count or 0) + (p.shares_count or 0)
        for p in posts
    ]
    E_median = statistics.median(engagement_list) if engagement_list else 0

    # Извлекаем специфичные для Telegram метрики из последнего snapshot
    telegram_specific = {}
    if end_snapshot and end_snapshot.extra_data:
        extra = end_snapshot.extra_data
        telegram_specific = {
            "avg_post_reach": extra.get("avg_post_reach", 0),
            "adv_post_reach_12h": extra.get("adv_post_reach_12h", 0),
            "adv_post_reach_24h": extra.get("adv_post_reach_24h", 0),
            "adv_post_reach_48h": extra.get("adv_post_reach_48h", 0),
            "err_percent": extra.get("err_percent", 0),
            "err24_percent": extra.get("err24_percent", 0),
            "er_percent": extra.get("er_percent", 0),
            "daily_reach": extra.get("daily_reach", 0),
            "ci_index": extra.get("ci_index", 0),
            "mentions_count": extra.get("mentions_count", 0),
            "forwards_count": extra.get("forwards_count", 0),
            "mentioning_channels_count": extra.get("mentioning_channels_count", 0),
        }

    return {
        # Срез профиля
        "F": F,
        "F_prev": F_prev,
        "delta_F": delta_F,
        "delta_F_percent": round(delta_F_percent, 2),
        # Контент
        "P": P,
        "V": V,
        "V_avg": round(V_avg, 2),
        "V_median": round(V_median, 2),
        # Вовлечённость
        "E": E,
        "E_avg": round(E_avg, 2),
        "E_median": round(E_median, 2),
        "ER_view": round(ER_view, 2),
        # Компоненты вовлечённости
        "total_reactions": total_reactions,
        "total_comments": total_comments,
        "total_shares": total_shares,
        # Telegram специфичные метрики
        "ERR_percent": round(ERR_percent, 2),
        "ER_percent": round(ER_percent, 2),
        **telegram_specific,
        # Средние показатели на пост
        "reactions_per_post": round(total_reactions / max(P, 1), 2) if P > 0 else 0,
        "comments_per_post": round(total_comments / max(P, 1), 2) if P > 0 else 0,
        "shares_per_post": round(total_shares / max(P, 1), 2) if P > 0 else 0,
    }


def _calculate_comparison_metrics(current: dict, previous: dict) -> dict:
    """Вычислить сравнительные метрики"""
    comparison = {}

    # Метрики для сравнения
    metrics_to_compare = [
        "F",
        "delta_F",
        "P",
        "V",
        "V_avg",
        "E",
        "E_avg",
        "ER_view",
        "ERR_percent",
        "ER_percent",
        "total_reactions",
        "total_comments",
        "total_shares",
        "avg_post_reach",
        "ci_index",
    ]

    for metric in metrics_to_compare:
        curr_val = current.get(metric, 0) or 0
        prev_val = previous.get(metric, 0) or 0

        delta = curr_val - prev_val
        delta_percent = (delta / max(abs(prev_val), 1)) * 100 if prev_val != 0 else 0

        comparison[f"{metric}_delta"] = round(delta, 2)
        comparison[f"{metric}_delta_percent"] = round(delta_percent, 2)

    return comparison


@router.get("/all-authors")
async def get_all_authors_telegram_analytics(
    current_start: datetime = Query(..., description="Начало текущего периода"),
    current_end: datetime = Query(..., description="Конец текущего периода"),
    previous_start: Optional[datetime] = Query(
        None, description="Начало прошлого периода для сравнения"
    ),
    previous_end: Optional[datetime] = Query(
        None, description="Конец прошлого периода для сравнения"
    ),
):
    """
    Получить аналитику по всем авторам с Telegram каналами

    Возвращает агрегированные данные по каждому автору
    """
    # Получаем всех авторов
    authors = await Author.all()

    authors_data = []
    total_aggregated = {
        "F": 0,
        "P": 0,
        "V": 0,
        "E": 0,
        "total_reactions": 0,
        "total_comments": 0,
        "total_shares": 0,
        "total_channels": 0,
        "err_percent_sum": 0,
        "er_percent_sum": 0,
        "ci_index_sum": 0,
        "avg_post_reach_sum": 0,
    }

    for author in authors:
        # Получаем Telegram каналы автора
        telegram_accounts = await SocialAccount.filter(
            author_id=author.id, platform="telegram", is_active=True
        ).all()

        if not telegram_accounts:
            continue

        author_aggregated = {
            "F": 0,
            "P": 0,
            "V": 0,
            "E": 0,
            "total_reactions": 0,
            "total_comments": 0,
            "total_shares": 0,
            "err_percent_sum": 0,
            "er_percent_sum": 0,
            "ci_index_sum": 0,
            "avg_post_reach_sum": 0,
            "channels_count": len(telegram_accounts),
        }

        channels_metrics = []

        for account in telegram_accounts:
            current_metrics = await _calculate_telegram_period_metrics(
                account, current_start, current_end
            )

            channels_metrics.append(
                {
                    "social_account_id": account.id,
                    "username": account.username,
                    "metrics": current_metrics,
                }
            )

            # Агрегируем
            author_aggregated["F"] += current_metrics.get("F", 0)
            author_aggregated["P"] += current_metrics.get("P", 0)
            author_aggregated["V"] += current_metrics.get("V", 0)
            author_aggregated["E"] += current_metrics.get("E", 0)
            author_aggregated["total_reactions"] += current_metrics.get(
                "total_reactions", 0
            )
            author_aggregated["total_comments"] += current_metrics.get(
                "total_comments", 0
            )
            author_aggregated["total_shares"] += current_metrics.get("total_shares", 0)
            author_aggregated["err_percent_sum"] += current_metrics.get(
                "ERR_percent", 0
            )
            author_aggregated["er_percent_sum"] += current_metrics.get("ER_percent", 0)
            author_aggregated["ci_index_sum"] += current_metrics.get("ci_index", 0)
            author_aggregated["avg_post_reach_sum"] += current_metrics.get(
                "avg_post_reach", 0
            )

        # Вычисляем средние значения
        channels_count = len(telegram_accounts)
        author_aggregated["err_percent_avg"] = (
            author_aggregated["err_percent_sum"] / channels_count
            if channels_count > 0
            else 0
        )
        author_aggregated["er_percent_avg"] = (
            author_aggregated["er_percent_sum"] / channels_count
            if channels_count > 0
            else 0
        )
        author_aggregated["ci_index_avg"] = (
            author_aggregated["ci_index_sum"] / channels_count
            if channels_count > 0
            else 0
        )
        author_aggregated["avg_post_reach_avg"] = (
            author_aggregated["avg_post_reach_sum"] / channels_count
            if channels_count > 0
            else 0
        )
        author_aggregated["V_avg"] = (
            author_aggregated["V"] / author_aggregated["P"]
            if author_aggregated["P"] > 0
            else 0
        )
        author_aggregated["E_avg"] = (
            author_aggregated["E"] / author_aggregated["P"]
            if author_aggregated["P"] > 0
            else 0
        )
        author_aggregated["ER_view"] = (
            (author_aggregated["E"] / author_aggregated["V"])
            if author_aggregated["V"] > 0
            else 0
        )

        authors_data.append(
            {
                "author_id": author.id,
                "author_name": author.name,
                "channels": channels_metrics,
                "aggregated_metrics": author_aggregated,
            }
        )

        # Агрегируем в общую сумму
        total_aggregated["F"] += author_aggregated["F"]
        total_aggregated["P"] += author_aggregated["P"]
        total_aggregated["V"] += author_aggregated["V"]
        total_aggregated["E"] += author_aggregated["E"]
        total_aggregated["total_reactions"] += author_aggregated["total_reactions"]
        total_aggregated["total_comments"] += author_aggregated["total_comments"]
        total_aggregated["total_shares"] += author_aggregated["total_shares"]
        total_aggregated["total_channels"] += channels_count
        total_aggregated["err_percent_sum"] += author_aggregated["err_percent_sum"]
        total_aggregated["er_percent_sum"] += author_aggregated["er_percent_sum"]
        total_aggregated["ci_index_sum"] += author_aggregated["ci_index_sum"]
        total_aggregated["avg_post_reach_sum"] += author_aggregated[
            "avg_post_reach_sum"
        ]

    # Вычисляем общие средние
    authors_count = len(authors_data)
    if authors_count > 0:
        total_aggregated["err_percent_avg"] = (
            total_aggregated["err_percent_sum"] / total_aggregated["total_channels"]
        )
        total_aggregated["er_percent_avg"] = (
            total_aggregated["er_percent_sum"] / total_aggregated["total_channels"]
        )
        total_aggregated["ci_index_avg"] = (
            total_aggregated["ci_index_sum"] / total_aggregated["total_channels"]
        )
        total_aggregated["avg_post_reach_avg"] = (
            total_aggregated["avg_post_reach_sum"] / total_aggregated["total_channels"]
        )
        total_aggregated["V_avg"] = (
            total_aggregated["V"] / total_aggregated["P"]
            if total_aggregated["P"] > 0
            else 0
        )
        total_aggregated["E_avg"] = (
            total_aggregated["E"] / total_aggregated["P"]
            if total_aggregated["P"] > 0
            else 0
        )
        total_aggregated["ER_view"] = (
            (total_aggregated["E"] / total_aggregated["V"])
            if total_aggregated["V"] > 0
            else 0
        )

    return {
        "period": {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "days": (current_end - current_start).days,
        },
        "authors": authors_data,
        "total_aggregated": total_aggregated,
        "authors_count": authors_count,
    }
