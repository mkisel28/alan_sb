from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from models import SocialAccount, ProfileSnapshot, Video
from schemas import SocialAccountAnalyticsResponse
from api.comparative_analytics import calculate_comparative_analytics
import statistics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/{social_account_id}", response_model=SocialAccountAnalyticsResponse)
async def get_social_account_analytics(
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
    Получить полную аналитику по социальному аккаунту

    Возвращает все метрики:
    - Срез профиля (F, ΔF, ΔF%)
    - Контент за период (P, V, V_avg)
    - Вовлечённость (E, E_avg, ER_view, ER_fol)
    - Вирусность (SR, CR)
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Вычисляем метрики для текущего периода
    current_metrics = await _calculate_period_metrics(
        social_account, current_start, current_end
    )

    # Вычисляем метрики для прошлого периода (если указан)
    previous_metrics = None
    comparison_metrics = None

    if previous_start and previous_end:
        previous_metrics = await _calculate_period_metrics(
            social_account, previous_start, previous_end
        )
        comparison_metrics = _calculate_comparison_metrics(
            current_metrics, previous_metrics
        )

    return SocialAccountAnalyticsResponse(
        social_account_id=social_account_id,
        platform=social_account.platform,
        current_period={
            "start": current_start,
            "end": current_end,
            "metrics": current_metrics,
        },
        previous_period={
            "start": previous_start,
            "end": previous_end,
            "metrics": previous_metrics,
        }
        if previous_metrics
        else None,
        comparison=comparison_metrics,
    )


async def _calculate_period_metrics(
    social_account: SocialAccount, period_start: datetime, period_end: datetime
) -> dict:
    """Вычислить все метрики за период"""

    # Нормализуем даты: period_end ставим на конец дня, чтобы включить все записи за этот день
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

    # Получаем все видео за период
    videos = await Video.filter(
        social_account=social_account,
        created_at_platform__gte=period_start,
        created_at_platform__lte=period_end,
    ).all()

    # P - количество публикаций
    P = len(videos)

    # V - суммарные просмотры
    V = sum(v.views_count or 0 for v in videos)

    # E - суммарная вовлечённость
    E = sum(
        (v.likes_count or 0)
        + (v.comments_count or 0)
        + (v.shares_count or 0)
        + (v.saves_count or 0)
        for v in videos
    )

    # Компоненты вовлечённости
    total_likes = sum(v.likes_count or 0 for v in videos)
    total_comments = sum(v.comments_count or 0 for v in videos)
    total_shares = sum(v.shares_count or 0 for v in videos)
    total_saves = sum(v.saves_count or 0 for v in videos)

    # V_avg - средние просмотры на пост
    V_avg = V / max(P, 1) if P > 0 else 0

    # E_avg - средняя вовлечённость на пост
    E_avg = E / max(P, 1) if P > 0 else 0

    # ER_view - вовлечённость на просмотр
    ER_view = (E / max(V, 1)) * 100 if V > 0 else 0

    # ER_fol - вовлечённость на подписчика
    ER_fol = (E / max(F, 1)) if F > 0 else 0

    # SR - доля репостов (share rate)
    SR = (total_shares / max(V, 1)) * 100 if V > 0 else 0

    # CR - доля комментариев (comment rate)
    CR = (total_comments / max(V, 1)) * 100 if V > 0 else 0

    # Медиана просмотров
    views_list = [v.views_count or 0 for v in videos if v.views_count]
    V_median = statistics.median(views_list) if views_list else 0

    # Медиана вовлечённости
    engagement_list = [
        (v.likes_count or 0)
        + (v.comments_count or 0)
        + (v.shares_count or 0)
        + (v.saves_count or 0)
        for v in videos
    ]
    E_median = statistics.median(engagement_list) if engagement_list else 0

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
        "ER_fol": round(ER_fol, 2),
        # Компоненты вовлечённости
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_saves": total_saves,
        # Вирусность
        "SR": round(SR, 4),
        "CR": round(CR, 4),
        # Дополнительные метрики
        "likes_per_post": round(total_likes / max(P, 1), 2) if P > 0 else 0,
        "comments_per_post": round(total_comments / max(P, 1), 2) if P > 0 else 0,
        "shares_per_post": round(total_shares / max(P, 1), 2) if P > 0 else 0,
    }


def _calculate_comparison_metrics(current: dict, previous: dict) -> dict:
    """Вычислить метрики сравнения (изменения между периодами)"""

    def safe_percent_change(current_val, prev_val):
        if prev_val == 0:
            return 0 if current_val == 0 else 100
        return ((current_val - prev_val) / prev_val) * 100

    return {
        # Изменения основных метрик
        "V_avg_change": safe_percent_change(current["V_avg"], previous["V_avg"]),
        "E_avg_change": safe_percent_change(current["E_avg"], previous["E_avg"]),
        "ER_view_change": safe_percent_change(current["ER_view"], previous["ER_view"]),
        "ER_fol_change": safe_percent_change(current["ER_fol"], previous["ER_fol"]),
        "P_change": current["P"] - previous["P"],
        # Изменения в процентах
        "V_change_percent": safe_percent_change(current["V"], previous["V"]),
        "E_change_percent": safe_percent_change(current["E"], previous["E"]),
        # Динамика вирусности
        "SR_change": current["SR"] - previous["SR"],
        "CR_change": current["CR"] - previous["CR"],
    }


@router.get("/comparative/platforms")
async def get_comparative_analytics(
    platforms: List[str] = Query(default=None),
    start_date: Optional[str] = Query(
        default=None, description="Дата начала периода (ISO: YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        default=None, description="Дата окончания периода (ISO: YYYY-MM-DD)"
    ),
    period: Optional[str] = Query(
        default="30d",
        description="Период: 7d, 30d, 90d, 365d (используется если не указаны start_date/end_date)",
    ),
    include_previous: bool = Query(
        default=True,
        description="Включить предыдущий период для расчета Momentum Score",
    ),
):
    """
    Сравнительная аналитика всех авторов по выбранным платформам

    Возвращает:
    - Метрики всех авторов по каждой платформе (F, ΔF, P, V, E, ER, SR, CR)
    - Presence Score (PS) - сила присутствия автора (0-100)
    - Momentum Score (MS) - ускорение роста автора (0-100)
    - Перцентили по ключевым метрикам
    - Агрегированную статистику по платформе

    PS = 0.35·pct(V_avg) + 0.35·pct(ER_view) + 0.20·pct(SR) + 0.10·pct(P)
    MS = 0.50·pct(ΔV_avg%) + 0.30·pct(ΔER%) + 0.20·pct(ΔF%)
    """
    if not platforms:
        raise HTTPException(
            status_code=400, detail="Необходимо выбрать хотя бы одну платформу"
        )

    try:
        period = period if not start_date else None
        result = await calculate_comparative_analytics(
            platforms=platforms,
            period=period,
            custom_start=start_date,
            custom_end=end_date,
            include_previous=include_previous,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
