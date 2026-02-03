"""
Сервис для сбора данных с YouTube через ScrapCreators API
"""

import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional
from models import SocialAccount, ProfileSnapshot, Video
from config import settings

SCRAPECREATORS_API_KEY = settings.scrapecreators_api_key
SCRAPECREATORS_BASE_URL = "https://api.scrapecreators.com/v1/youtube"


async def collect_youtube_channel_data(
    social_account: SocialAccount,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Собрать записи канала YouTube за указанный период

    Args:
        social_account: Аккаунт YouTube канала
        start_date: Дата начала периода (по умолчанию - 30 дней назад)
        end_date: Дата окончания периода (по умолчанию - сегодня)
    """
    if social_account.platform not in ["youtube", "youtube_shorts"]:
        raise ValueError("Social account must be YouTube or YouTube Shorts platform")

    # Устанавливаем дефолтные даты если не указаны
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    else:
        # Если дата передана без timezone, делаем её UTC-aware
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

    if start_date is None:
        start_date = end_date - timedelta(days=30)
    else:
        # Если дата передана без timezone, делаем её UTC-aware
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

    channel_id = social_account.platform_user_id
    credits_used = 0
    posts_collected = 0
    profile_updated = False

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Получаем информацию о канале
        channel_response = await client.get(
            f"{SCRAPECREATORS_BASE_URL}/channel",
            params={"channelId": channel_id},
            headers={"x-api-key": SCRAPECREATORS_API_KEY},
        )
        channel_response.raise_for_status()
        channel_data = channel_response.json()
        credits_used += 1

        # Сохраняем snapshot профиля
        if channel_data.get("success"):
            await _save_channel_snapshot(social_account, channel_data)
            profile_updated = True

            # Обновляем username если не задан
            if not social_account.username and channel_data.get("name"):
                social_account.username = channel_data["name"]
                await social_account.save()

        # 2. Собираем записи в зависимости от типа платформы
        if social_account.platform == "youtube_shorts":
            # Собираем Shorts
            videos_data = await _collect_shorts(
                client, channel_id, start_date, end_date
            )
        else:
            # Собираем обычные видео
            videos_data = await _collect_videos(
                client, channel_id, start_date, end_date
            )

        credits_used += len(videos_data) // 50 + 1  # Примерная оценка

        # 3. Сохраняем записи
        for video_data in videos_data:
            await _save_youtube_video(social_account, video_data)
            posts_collected += 1

    return {
        "success": True,
        "message": f"Collected {posts_collected} posts from {start_date.date()} to {end_date.date()}",
        "posts_collected": posts_collected,
        "profile_updated": profile_updated,
        "credits_remaining": channel_data.get("credits_remaining"),
    }


async def _collect_videos(
    client: httpx.AsyncClient, channel_id: str, start_date: datetime, end_date: datetime
) -> list:
    """Собрать обычные видео канала за указанный период"""
    all_videos = []
    continuation_token = None

    while True:
        params = {
            "channelId": channel_id,
            "sort": "latest",
            "includeExtras": "true",
        }
        if continuation_token:
            params["continuationToken"] = continuation_token

        response = await client.get(
            f"{SCRAPECREATORS_BASE_URL}/channel-videos",
            params=params,
            headers={"x-api-key": SCRAPECREATORS_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or not data.get("videos"):
            break

        videos = data["videos"]

        # Фильтруем и проверяем даты
        for video in videos:
            # Парсим дату публикации
            publish_date_str = video.get("publishDate") or video.get("publishedTime")
            try:
                video_date = datetime.fromisoformat(
                    publish_date_str.replace("Z", "+00:00")
                )

                # Проверяем диапазон дат
                if video_date < start_date:
                    # Достигли начальной даты - прекращаем сбор
                    return all_videos

                if video_date <= end_date:
                    all_videos.append(video)
            except (ValueError, AttributeError):
                # Если не удалось распарсить дату, добавляем видео
                all_videos.append(video)

        # Проверяем наличие continuationToken для пагинации
        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break

    return all_videos


async def _collect_shorts(
    client: httpx.AsyncClient, channel_id: str, start_date: datetime, end_date: datetime
) -> list:
    """Собрать Shorts канала за указанный период"""
    all_shorts = []
    continuation_token = None

    while True:
        params = {
            "channelId": channel_id,
            "sort": "newest",
        }
        if continuation_token:
            params["continuationToken"] = continuation_token

        response = await client.get(
            f"{SCRAPECREATORS_BASE_URL}/channel/shorts",
            params=params,
            headers={"x-api-key": SCRAPECREATORS_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or not data.get("shorts"):
            break

        shorts = data["shorts"]

        # Фильтруем и проверяем даты
        for short in shorts:
            # Парсим дату публикации
            publish_date_str = short.get("publishDate") or short.get("publishedTime")
            try:
                short_date = datetime.fromisoformat(
                    publish_date_str.replace("Z", "+00:00")
                )

                # Проверяем диапазон дат
                if short_date < start_date:
                    # Достигли начальной даты - прекращаем сбор
                    return all_shorts

                if short_date <= end_date:
                    all_shorts.append(short)
            except (ValueError, AttributeError):
                # Если не удалось распарсить дату, добавляем short
                all_shorts.append(short)

        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break

    return all_shorts


async def _save_channel_snapshot(
    social_account: SocialAccount, channel_data: dict
) -> ProfileSnapshot:
    """Сохранить снимок профиля канала"""
    # Ищем аватар (берем самый большой)
    avatar_url = None
    if channel_data.get("avatar", {}).get("image", {}).get("sources"):
        sources = channel_data["avatar"]["image"]["sources"]
        avatar_url = sources[-1]["url"] if sources else None

    snapshot = await ProfileSnapshot.create(
        social_account=social_account,
        snapshot_date=datetime.now(timezone.utc),
        followers_count=channel_data.get("subscriberCount", 0),
        following_count=0,  # YouTube не показывает подписки канала
        total_likes=0,  # YouTube API не предоставляет общее количество лайков
        total_posts=channel_data.get("videoCount", 0),
        avatar_url=avatar_url,
    )

    return snapshot


async def _save_youtube_video(social_account: SocialAccount, video_data: dict) -> Video:
    """Сохранить или обновить видео"""
    video_id = video_data.get("id")

    # Парсим дату публикации
    publish_date_str = video_data.get("publishDate") or video_data.get("publishedTime")
    try:
        created_at_platform = datetime.fromisoformat(
            publish_date_str.replace("Z", "+00:00")
        )
    except (ValueError, AttributeError):
        created_at_platform = datetime.now(timezone.utc)

    # Проверяем существование видео
    existing_video = await Video.filter(
        social_account=social_account, platform_video_id=video_id
    ).first()

    video_data_dict = {
        "social_account": social_account,
        "platform_video_id": video_id,
        "platform_author_id": social_account.platform_user_id,
        "description": video_data.get("description") or video_data.get("title"),
        "created_at_platform": created_at_platform,
        "video_url": video_data.get("url"),
        "share_url": video_data.get("url"),
        "cover_url": video_data.get("thumbnail"),
        "thumbnail_url": video_data.get("thumbnail"),
        "duration_ms": video_data.get("lengthSeconds", 0) * 1000
        if video_data.get("lengthSeconds")
        else None,
        "views_count": video_data.get("viewCountInt", 0),
        "likes_count": video_data.get("likeCountInt", 0),
        "comments_count": video_data.get("commentCountInt", 0),
        "shares_count": 0,  # YouTube API не предоставляет количество репостов
        "saves_count": 0,  # YouTube API не предоставляет количество сохранений
        "last_updated": datetime.now(timezone.utc),
    }

    if existing_video:
        # Обновляем существующее видео
        for key, value in video_data_dict.items():
            if key != "social_account":  # Не обновляем foreign key
                setattr(existing_video, key, value)
        await existing_video.save()
        return existing_video
    else:
        # Создаем новое видео
        video = await Video.create(**video_data_dict)
        return video
