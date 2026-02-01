from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from models import SocialAccount, ProfileSnapshot, Video
import numpy as np
from scipy import stats


def calculate_percentile(values: List[float], value: float) -> float:
    """
    Вычисляет перцентиль значения в массиве

    Args:
        values: Список всех значений для сравнения
        value: Значение для которого вычисляется перцентиль

    Returns:
        Перцентиль от 0 до 100
    """
    if not values or len(values) == 0:
        return 50.0

    # Убираем None и NaN
    clean_values = [v for v in values if v is not None and not np.isnan(v)]
    if not clean_values:
        return 50.0

    if value is None or np.isnan(value):
        return 0.0

    # Используем scipy для точного расчета перцентиля

    percentile = stats.percentileofscore(clean_values, value, kind="rank")
    return float(percentile)


def get_period_dates(
    period: Optional[str] = None,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None,
) -> Tuple[datetime, datetime]:
    """
    Возвращает даты начала и конца периода

    Args:
        period: '7d', '30d', '90d', '365d', 'previous' или None (если используются custom даты)
        custom_start: Начальная дата для custom периода (ISO: YYYY-MM-DD)
        custom_end: Конечная дата для custom периода (ISO: YYYY-MM-DD)

    Returns:
        Tuple (start_date, end_date)
    """
    # Если переданы custom даты - используем их в первую очередь
    if custom_start and custom_end:
        start_date = datetime.fromisoformat(custom_start.replace("Z", "+00:00"))
        end_date = datetime.fromisoformat(custom_end.replace("Z", "+00:00"))
        return start_date, end_date

    # Иначе используем period
    end_date = datetime.now()

    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    elif period == "365d":
        start_date = end_date - timedelta(days=365)
    elif period == "previous":
        # Предыдущий период той же длины
        # По умолчанию берем предыдущие 30 дней
        end_date = datetime.now() - timedelta(days=30)
        start_date = end_date - timedelta(days=30)
    else:
        # По умолчанию 30 дней
        start_date = end_date - timedelta(days=30)

    return start_date, end_date


async def calculate_author_metrics(
    social_account_id: int,
    start_date: datetime,
    end_date: datetime,
    prev_start_date: Optional[datetime] = None,
    prev_end_date: Optional[datetime] = None,
) -> Dict:
    """
    Рассчитывает все метрики для автора за период

    Returns:
        Dict с метриками: F, ΔF, ΔF%, P, V, V_avg, E, E_avg, ER_view, ER_fol, SR, CR
    """
    social_account = await SocialAccount.get(id=social_account_id)

    # Получаем snapshot на конец периода (F - Followers)
    end_snapshot = (
        await ProfileSnapshot.filter(
            social_account=social_account, snapshot_date__lte=end_date
        )
        .order_by("-snapshot_date")
        .first()
    )

    F = end_snapshot.followers_count if end_snapshot else 0

    # Получаем snapshot на начало периода (для расчета ΔF)
    start_snapshot = (
        await ProfileSnapshot.filter(
            social_account=social_account, snapshot_date__lte=start_date
        )
        .order_by("-snapshot_date")
        .first()
    )

    F_prev = start_snapshot.followers_count if start_snapshot else 0

    # ΔF (абсолютный рост подписчиков)
    delta_F = F - F_prev

    # ΔF% (процентный рост подписчиков)
    delta_F_percent = (delta_F / max(F_prev, 1)) if F_prev > 0 else 0

    # Получаем видео за период
    videos = await Video.filter(
        social_account=social_account,
        created_at_platform__gte=start_date,
        created_at_platform__lte=end_date,
    ).all()

    # P (количество публикаций)
    P = len(videos)

    # V (суммарные просмотры)
    V = sum(v.views_count for v in videos)

    # E (суммарная вовлеченность: лайки + комментарии + репосты + сохранения)
    E = sum(
        v.likes_count + v.comments_count + v.shares_count + (v.saves_count or 0)
        for v in videos
    )

    # Shares и Comments отдельно для SR и CR
    total_shares = sum(v.shares_count for v in videos)
    total_comments = sum(v.comments_count for v in videos)

    # V_avg (средние просмотры на пост)
    V_avg = V / max(P, 1)

    # E_avg (средняя вовлеченность на пост)
    E_avg = E / max(P, 1)

    # ER_view (вовлеченность на просмотр)
    ER_view = E / max(V, 1)

    # ER_fol (вовлеченность на подписчика)
    ER_fol = E / max(F, 1)

    # SR (Share Rate - доля репостов)
    SR = total_shares / max(V, 1)

    # CR (Comment Rate - доля комментариев)
    CR = total_comments / max(V, 1)

    result = {
        "F": F,
        "delta_F": delta_F,
        "delta_F_percent": delta_F_percent,
        "P": P,
        "V": V,
        "V_avg": V_avg,
        "E": E,
        "E_avg": E_avg,
        "ER_view": ER_view,
        "ER_fol": ER_fol,
        "SR": SR,
        "CR": CR,
        "total_shares": total_shares,
        "total_comments": total_comments,
    }

    # Если есть предыдущий период, рассчитываем метрики для него
    if prev_start_date and prev_end_date:
        prev_metrics = await calculate_author_metrics(
            social_account_id, prev_start_date, prev_end_date
        )

        # Рассчитываем изменения метрик для Momentum Score
        delta_V_avg_percent = (V_avg - prev_metrics["V_avg"]) / max(
            prev_metrics["V_avg"], 0.001
        )
        delta_ER_percent = (ER_view - prev_metrics["ER_view"]) / max(
            prev_metrics["ER_view"], 0.000001
        )

        result["prev_metrics"] = prev_metrics
        result["delta_V_avg_percent"] = delta_V_avg_percent
        result["delta_ER_percent"] = delta_ER_percent

    return result


async def calculate_comparative_analytics(
    platforms: List[str],
    period: str | None = "30d",
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None,
    include_previous: bool = True,
) -> Dict:
    """
    Рассчитывает сравнительную аналитику по выбранным платформам

    Args:
        platforms: Список платформ ['tiktok', 'youtube', 'youtube_shorts', ...]
        period: Период анализа
        custom_start: Начальная дата для custom периода
        custom_end: Конечная дата для custom периода
        include_previous: Включить ли предыдущий период для расчета MS

    Returns:
        Dict с данными по каждой платформе и авторам
    """
    # Получаем даты текущего периода
    start_date, end_date = get_period_dates(period, custom_start, custom_end)

    # Получаем даты предыдущего периода (той же длины)
    if include_previous:
        period_length = (end_date - start_date).days
        prev_end_date = start_date
        prev_start_date = start_date - timedelta(days=period_length)
    else:
        prev_start_date = None
        prev_end_date = None

    result = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": (end_date - start_date).days,
        },
        "platforms": {},
    }

    if include_previous:
        result["previous_period"] = {
            "start": prev_start_date.isoformat(),
            "end": prev_end_date.isoformat(),
            "days": (prev_end_date - prev_start_date).days,
        }

    # Обрабатываем каждую платформу
    for platform in platforms:
        # Получаем всех авторов с активными аккаунтами на этой платформе
        social_accounts = (
            await SocialAccount.filter(platform=platform, is_active=True)
            .prefetch_related("author")
            .all()
        )

        if not social_accounts:
            continue

        platform_data = {"platform": platform, "authors": [], "aggregated": {}}

        authors_metrics = []

        # Рассчитываем метрики для каждого автора
        for account in social_accounts:
            metrics = await calculate_author_metrics(
                account.id, start_date, end_date, prev_start_date, prev_end_date
            )

            author_data = {
                "author_id": account.author.id,
                "author_name": account.author.name,
                "social_account_id": account.id,
                "username": account.username,
                "metrics": metrics,
            }

            authors_metrics.append(author_data)

        # Собираем все значения метрик для расчета перцентилей
        V_avg_values = [a["metrics"]["V_avg"] for a in authors_metrics]
        ER_view_values = [a["metrics"]["ER_view"] for a in authors_metrics]
        SR_values = [a["metrics"]["SR"] for a in authors_metrics]
        P_values = [a["metrics"]["P"] for a in authors_metrics]
        F_values = [a["metrics"]["F"] for a in authors_metrics]

        # Если есть предыдущий период, собираем значения метрик для предыдущего периода
        prev_V_avg_values = []
        prev_ER_view_values = []
        prev_SR_values = []
        prev_P_values = []
        prev_F_values = []

        if include_previous:
            prev_V_avg_values = [
                a["metrics"]["prev_metrics"]["V_avg"]
                for a in authors_metrics
                if "prev_metrics" in a["metrics"]
            ]
            prev_ER_view_values = [
                a["metrics"]["prev_metrics"]["ER_view"]
                for a in authors_metrics
                if "prev_metrics" in a["metrics"]
            ]
            prev_SR_values = [
                a["metrics"]["prev_metrics"]["SR"]
                for a in authors_metrics
                if "prev_metrics" in a["metrics"]
            ]
            prev_P_values = [
                a["metrics"]["prev_metrics"]["P"]
                for a in authors_metrics
                if "prev_metrics" in a["metrics"]
            ]
            prev_F_values = [
                a["metrics"]["prev_metrics"]["F"]
                for a in authors_metrics
                if "prev_metrics" in a["metrics"]
            ]

        # Рассчитываем Presence Score (PS) для каждого автора
        for author_data in authors_metrics:
            m = author_data["metrics"]

            # Перцентили для PS (текущий период)
            pct_V_avg = calculate_percentile(V_avg_values, m["V_avg"])
            pct_ER_view = calculate_percentile(ER_view_values, m["ER_view"])
            pct_SR = calculate_percentile(SR_values, m["SR"])
            pct_P = calculate_percentile(P_values, m["P"])
            pct_F = calculate_percentile(F_values, m["F"])

            # PS = 0.25·pct(V_avg) + 0.25·pct(ER_view) + 0.15·pct(SR) + 0.10·pct(P) + 0.25·pct(F)
            # Добавлен перцентиль подписчиков (F) с весом 25% для учета масштаба влияния
            PS = (
                0.25 * pct_V_avg
                + 0.25 * pct_ER_view
                + 0.15 * pct_SR
                + 0.10 * pct_P
                + 0.25 * pct_F
            )

            author_data["scores"] = {
                "PS": round(PS, 2),
                "percentiles": {
                    "V_avg": round(pct_V_avg, 2),
                    "ER_view": round(pct_ER_view, 2),
                    "SR": round(pct_SR, 2),
                    "P": round(pct_P, 2),
                    "F": round(pct_F, 2),
                },
            }

            # Рассчитываем PS для предыдущего периода
            if include_previous and "prev_metrics" in m and len(prev_V_avg_values) > 0:
                prev_m = m["prev_metrics"]

                # Перцентили для prev_PS
                prev_pct_V_avg = calculate_percentile(
                    prev_V_avg_values, prev_m["V_avg"]
                )
                prev_pct_ER_view = calculate_percentile(
                    prev_ER_view_values, prev_m["ER_view"]
                )
                prev_pct_SR = calculate_percentile(prev_SR_values, prev_m["SR"])
                prev_pct_P = calculate_percentile(prev_P_values, prev_m["P"])
                prev_pct_F = calculate_percentile(prev_F_values, prev_m["F"])

                # prev_PS с той же формулой
                prev_PS = (
                    0.25 * prev_pct_V_avg
                    + 0.25 * prev_pct_ER_view
                    + 0.15 * prev_pct_SR
                    + 0.10 * prev_pct_P
                    + 0.25 * prev_pct_F
                )

                author_data["scores"]["prev_PS"] = round(prev_PS, 2)
                author_data["scores"]["prev_percentiles"] = {
                    "V_avg": round(prev_pct_V_avg, 2),
                    "ER_view": round(prev_pct_ER_view, 2),
                    "SR": round(prev_pct_SR, 2),
                    "P": round(prev_pct_P, 2),
                    "F": round(prev_pct_F, 2),
                }

            # Рассчитываем Momentum Score (MS) если есть предыдущий период
            if include_previous and "delta_V_avg_percent" in m:
                delta_V_avg_values = [
                    a["metrics"].get("delta_V_avg_percent", 0)
                    for a in authors_metrics
                    if "delta_V_avg_percent" in a["metrics"]
                ]
                delta_ER_values = [
                    a["metrics"].get("delta_ER_percent", 0)
                    for a in authors_metrics
                    if "delta_ER_percent" in a["metrics"]
                ]
                delta_F_values = [
                    a["metrics"]["delta_F_percent"] for a in authors_metrics
                ]

                pct_delta_V_avg = calculate_percentile(
                    delta_V_avg_values, m.get("delta_V_avg_percent", 0)
                )
                pct_delta_ER = calculate_percentile(
                    delta_ER_values, m.get("delta_ER_percent", 0)
                )
                pct_delta_F = calculate_percentile(delta_F_values, m["delta_F_percent"])

                # MS = 0.50·pct(ΔV_avg%) + 0.30·pct(ΔER%) + 0.20·pct(ΔF%)
                MS = 0.50 * pct_delta_V_avg + 0.30 * pct_delta_ER + 0.20 * pct_delta_F

                author_data["scores"]["MS"] = round(MS, 2)
                author_data["scores"]["momentum_percentiles"] = {
                    "delta_V_avg": round(pct_delta_V_avg, 2),
                    "delta_ER": round(pct_delta_ER, 2),
                    "delta_F": round(pct_delta_F, 2),
                }

        # Сортируем авторов по PS (от лучших к худшим)
        authors_metrics.sort(key=lambda x: x["scores"]["PS"], reverse=True)

        platform_data["authors"] = authors_metrics

        # Агрегированная статистика по платформе
        if authors_metrics:
            total_followers = sum(a["metrics"]["F"] for a in authors_metrics)
            total_posts = sum(a["metrics"]["P"] for a in authors_metrics)
            total_views = sum(a["metrics"]["V"] for a in authors_metrics)
            total_engagement = sum(a["metrics"]["E"] for a in authors_metrics)

            platform_data["aggregated"] = {
                "total_authors": len(authors_metrics),
                "total_followers": total_followers,
                "total_posts": total_posts,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "avg_PS": round(
                    sum(a["scores"]["PS"] for a in authors_metrics)
                    / len(authors_metrics),
                    2,
                ),
                "avg_ER_view": round(
                    sum(a["metrics"]["ER_view"] for a in authors_metrics)
                    / len(authors_metrics),
                    4,
                ),
            }

            if include_previous:
                # Рассчитываем метрики предыдущего периода
                prev_total_followers = sum(
                    a["metrics"].get("prev_metrics", {}).get("F", 0)
                    for a in authors_metrics
                )
                prev_total_posts = sum(
                    a["metrics"].get("prev_metrics", {}).get("P", 0)
                    for a in authors_metrics
                )
                prev_total_views = sum(
                    a["metrics"].get("prev_metrics", {}).get("V", 0)
                    for a in authors_metrics
                )
                prev_total_engagement = sum(
                    a["metrics"].get("prev_metrics", {}).get("E", 0)
                    for a in authors_metrics
                )
                prev_avg_ER_view = sum(
                    a["metrics"].get("prev_metrics", {}).get("ER_view", 0)
                    for a in authors_metrics
                ) / len(authors_metrics)

                # Рассчитываем дельты
                delta_followers = total_followers - prev_total_followers
                delta_posts = total_posts - prev_total_posts
                delta_views = total_views - prev_total_views
                delta_engagement = total_engagement - prev_total_engagement
                delta_ER_view = (
                    platform_data["aggregated"]["avg_ER_view"] - prev_avg_ER_view
                )

                # Рассчитываем проценты изменения
                delta_followers_percent = (
                    (delta_followers / prev_total_followers * 100)
                    if prev_total_followers > 0
                    else 0
                )
                delta_posts_percent = (
                    (delta_posts / prev_total_posts * 100)
                    if prev_total_posts > 0
                    else 0
                )
                delta_views_percent = (
                    (delta_views / prev_total_views * 100)
                    if prev_total_views > 0
                    else 0
                )
                delta_engagement_percent = (
                    (delta_engagement / prev_total_engagement * 100)
                    if prev_total_engagement > 0
                    else 0
                )
                delta_ER_view_percent = (
                    (delta_ER_view / prev_avg_ER_view * 100)
                    if prev_avg_ER_view > 0
                    else 0
                )

                platform_data["aggregated"]["avg_MS"] = round(
                    sum(a["scores"].get("MS", 0) for a in authors_metrics)
                    / len(authors_metrics),
                    2,
                )

                # Добавляем дельты в aggregated
                platform_data["aggregated"]["deltas"] = {
                    "followers": {
                        "absolute": delta_followers,
                        "percent": round(delta_followers_percent, 2),
                    },
                    "posts": {
                        "absolute": delta_posts,
                        "percent": round(delta_posts_percent, 2),
                    },
                    "views": {
                        "absolute": delta_views,
                        "percent": round(delta_views_percent, 2),
                    },
                    "engagement": {
                        "absolute": delta_engagement,
                        "percent": round(delta_engagement_percent, 2),
                    },
                    "ER_view": {
                        "absolute": round(delta_ER_view, 4),
                        "percent": round(delta_ER_view_percent, 2),
                    },
                }

        result["platforms"][platform] = platform_data

    return result
