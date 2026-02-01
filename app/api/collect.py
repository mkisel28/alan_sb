from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from models import SocialAccount, Video
from schemas import (
    CollectDataRequest,
    CollectDataResponse,
    VideoResponse,
    ProfileSnapshotResponse,
)
from services.tiktok_service import TikTokService
from services.youtube_service import collect_youtube_channel_data
from services.instagram_service import collect_instagram_profile_data
from services.telegram_service import collect_telegram_channel_data

router = APIRouter(prefix="/api/collect", tags=["collect"])


@router.post("/tiktok/{social_account_id}", response_model=CollectDataResponse)
async def collect_tiktok_data(
    social_account_id: int, request: CollectDataRequest = CollectDataRequest()
):
    """
    Собрать данные TikTok профиля за указанный период

    - Получает видео через ScrapeCreators API
    - Сохраняет снимок профиля
    - Сохраняет видео и их метрики
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Проверяем платформу
    if social_account.platform != "tiktok":
        raise HTTPException(
            status_code=400, detail="This endpoint only supports TikTok accounts"
        )

    # Собираем данные
    try:
        tiktok_service = TikTokService()
        result = await tiktok_service.collect_videos(
            social_account=social_account,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return CollectDataResponse(
            success=True,
            message=result["message"],
            posts_collected=result["posts_collected"],
            profile_updated=result["profile_updated"],
            credits_remaining=result.get("credits_remaining"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting data: {str(e)}")


@router.post("/youtube/{social_account_id}", response_model=CollectDataResponse)
async def collect_youtube_data(
    social_account_id: int, request: CollectDataRequest = CollectDataRequest()
):
    """
    Собрать данные YouTube канала (обычные видео или Shorts) за указанный период

    - Получает информацию о канале
    - Получает видео или Shorts в зависимости от типа платформы
    - Сохраняет снимок профиля
    - Сохраняет видео и их метрики
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Проверяем платформу
    if social_account.platform not in ["youtube", "youtube_shorts"]:
        raise HTTPException(
            status_code=400,
            detail="This endpoint only supports YouTube and YouTube Shorts accounts",
        )

    # Собираем данные
    try:
        result = await collect_youtube_channel_data(
            social_account=social_account,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return CollectDataResponse(
            success=True,
            message=result["message"],
            posts_collected=result["posts_collected"],
            profile_updated=result["profile_updated"],
            credits_remaining=result.get("credits_remaining"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting data: {str(e)}")


@router.post("/instagram/{social_account_id}", response_model=CollectDataResponse)
async def collect_instagram_data(
    social_account_id: int, request: CollectDataRequest = CollectDataRequest()
):
    """
    Собрать данные Instagram профиля за указанный период

    - Получает информацию о профиле
    - Получает посты (фото и видео)
    - Сохраняет снимок профиля
    - Сохраняет посты и их метрики
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Проверяем платформу
    if social_account.platform != "instagram":
        raise HTTPException(
            status_code=400,
            detail="This endpoint only supports Instagram accounts",
        )

    # Собираем данные
    try:
        result = await collect_instagram_profile_data(
            social_account=social_account,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return CollectDataResponse(
            success=True,
            message=result["message"],
            posts_collected=result["posts_collected"],
            profile_updated=result["profile_updated"],
            credits_remaining=result.get("credits_remaining"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting data: {str(e)}")


@router.post("/telegram/{social_account_id}", response_model=CollectDataResponse)
async def collect_telegram_data(
    social_account_id: int, request: CollectDataRequest = CollectDataRequest()
):
    """
    Собрать данные Telegram канала за указанный период

    - Получает информацию о канале
    - Получает посты за указанный период
    - Получает детальную статистику постов
    - Сохраняет снимок профиля
    - Сохраняет посты и их метрики
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Проверяем платформу
    if social_account.platform != "telegram":
        raise HTTPException(
            status_code=400,
            detail="This endpoint only supports Telegram accounts",
        )

    # Собираем данные
    try:
        result = await collect_telegram_channel_data(
            social_account=social_account,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return CollectDataResponse(
            success=True,
            message=result["message"],
            posts_collected=result["posts_collected"],
            profile_updated=result["profile_updated"],
            credits_remaining=None,  # TGStat не использует кредиты таким образом
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting data: {str(e)}")


@router.get("/videos/{social_account_id}", response_model=List[VideoResponse])
async def get_account_videos(
    social_account_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("date", regex="^(date|views|likes|comments|shares)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    """
    Получить видео социального аккаунта

    - sort_by: date (дата публикации), views, likes, comments, shares
    - order: asc (возрастание), desc (убывание)
    - date_from/date_to: фильтр по дате публикации
    """
    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Базовый запрос
    query = Video.filter(social_account_id=social_account_id)

    # Фильтр по датам
    if date_from:
        query = query.filter(created_at_platform__gte=date_from)
    if date_to:
        query = query.filter(created_at_platform__lte=date_to)

    # Сортировка
    sort_field_map = {
        "date": "created_at_platform",
        "views": "views_count",
        "likes": "likes_count",
        "comments": "comments_count",
        "shares": "shares_count",
    }

    sort_field = sort_field_map[sort_by]
    if order == "desc":
        sort_field = f"-{sort_field}"

    videos = await query.order_by(sort_field).limit(limit).offset(offset).all()

    return [
        VideoResponse.model_validate(video, from_attributes=True) for video in videos
    ]


@router.get(
    "/profile-snapshots/{social_account_id}",
    response_model=List[ProfileSnapshotResponse],
)
async def get_profile_snapshots(social_account_id: int, limit: int = 30):
    """Получить историю снимков профиля"""
    from models import ProfileSnapshot

    # Проверяем существование аккаунта
    social_account = await SocialAccount.filter(id=social_account_id).first()
    if not social_account:
        raise HTTPException(status_code=404, detail="Social account not found")

    snapshots = (
        await ProfileSnapshot.filter(social_account_id=social_account_id)
        .order_by("-snapshot_date")
        .limit(limit)
        .all()
    )

    return [
        ProfileSnapshotResponse.model_validate(snapshot, from_attributes=True)
        for snapshot in snapshots
    ]
