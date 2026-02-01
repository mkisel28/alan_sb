"""
Сервис для сбора данных с Telegram через TGStat API
"""

import httpx
from datetime import datetime
from typing import Optional
from models import SocialAccount, ProfileSnapshot, Video
from config import settings

TGSTAT_API_TOKEN = settings.tgstat_api_token
TGSTAT_BASE_URL = "https://api.tgstat.ru"


async def collect_telegram_channel_data(
    social_account: SocialAccount,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Собрать данные канала Telegram за указанный период

    Args:
        social_account: Аккаунт Telegram канала
        start_date: Дата начала периода (по умолчанию - 30 дней назад)
        end_date: Дата окончания периода (по умолчанию - сегодня)

    Returns:
        dict с информацией о собранных данных
    """
    if social_account.platform != "telegram":
        raise ValueError("Social account must be Telegram platform")

    if not TGSTAT_API_TOKEN:
        raise ValueError(
            "TGStat API token is not configured. Please set TGSTAT_API_TOKEN in .env file"
        )

    channel_id = social_account.platform_user_id

    # Устанавливаем дефолтные даты если не указаны
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        from datetime import timedelta

        start_date = end_date - timedelta(days=30)

    posts_collected = 0
    profile_updated = False

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Получаем информацию о канале
        channel_stats = await _get_channel_stats(client, channel_id)

        # Сохраняем snapshot профиля
        if channel_stats:
            await _save_channel_snapshot(social_account, channel_stats)
            profile_updated = True

            # Обновляем username если не задан
            if not social_account.username and channel_stats.get("username"):
                social_account.username = channel_stats["username"]
                await social_account.save()

        # 2. Собираем посты за период
        posts_data = await _collect_posts_by_date(
            client, channel_id, start_date, end_date
        )

        # 3. Получаем детальную статистику для постов (если нужно)
        # Разбиваем на батчи по 50 постов
        for i in range(0, len(posts_data), 50):
            batch = posts_data[i : i + 50]
            post_ids = [post.get("id") for post in batch if post.get("id")]

            if post_ids:
                detailed_stats = await _get_posts_detailed_stats(
                    client, channel_id, post_ids
                )

                # Обогащаем данные постов детальной статистикой
                for post in batch:
                    post_id = post.get("id")
                    if post_id and post_id in detailed_stats:
                        post["detailed_stats"] = detailed_stats[post_id]

        # 4. Сохраняем посты
        for post_data in posts_data:
            await _save_telegram_post(social_account, post_data)
            posts_collected += 1

    return {
        "success": True,
        "message": f"Собрано {posts_collected} записей за период с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}",
        "posts_collected": posts_collected,
        "profile_updated": profile_updated,
        "channel_stats": channel_stats,
    }


async def _get_channel_stats(client: httpx.AsyncClient, channel_id: str) -> dict:
    """Получить статистику канала"""
    response = await client.get(
        f"{TGSTAT_BASE_URL}/channels/stat",
        params={"token": TGSTAT_API_TOKEN, "channelId": channel_id},
    )
    response.raise_for_status()
    data = response.json()

    if data.get("status") == "ok":
        return data.get("response", {})

    error_msg = data.get("error", "Unknown error")
    raise ValueError(f"TGStat API error: {error_msg}")


async def _collect_posts_by_date(
    client: httpx.AsyncClient,
    channel_id: str,
    start_date: datetime,
    end_date: datetime,
) -> list:
    """Собрать посты канала за указанный период"""
    all_posts = []
    offset = 0
    limit = 50

    # Конвертируем даты в timestamp
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    while True:
        params = {
            "token": TGSTAT_API_TOKEN,
            "channelId": channel_id,
            "limit": limit,
            "offset": offset,
            "startTime": start_timestamp,
            "endTime": end_timestamp,
            "hideForwards": 0,  # Не скрываем репосты
            "hideDeleted": 1,  # Скрываем удаленные
            "extended": 1,  # Получаем расширенную информацию
        }

        response = await client.get(
            f"{TGSTAT_BASE_URL}/channels/posts",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            error_msg = data.get("error", "Unknown error")
            raise ValueError(f"TGStat API error: {error_msg}")

        response_data = data.get("response", {})
        items = response_data.get("items", [])

        if not items:
            break

        # Проверяем дату последнего поста в батче
        last_post_date = items[-1].get("date", 0)

        all_posts.extend(items)

        # Если достигли начальной даты или нет больше постов
        if last_post_date < start_timestamp:
            # Фильтруем посты которые вне диапазона
            all_posts = [
                p
                for p in all_posts
                if start_timestamp <= p.get("date", 0) <= end_timestamp
            ]
            break

        count = response_data.get("count", 0)
        if count < limit:
            break

        offset += limit

        # Защита от бесконечного цикла (максимум 1000 постов согласно API)
        if offset >= 1000:
            break

    return all_posts


async def _get_posts_detailed_stats(
    client: httpx.AsyncClient, channel_id: str, post_ids: list
) -> dict:
    """Получить детальную статистику для нескольких постов"""
    try:
        params = {
            "token": TGSTAT_API_TOKEN,
            "channelId": channel_id,
            "postsIds": ",".join(map(str, post_ids)),
        }

        response = await client.get(
            f"{TGSTAT_BASE_URL}/posts/stat-multi",
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        print(data)
        if data.get("status") == "ok":
            # Преобразуем список в словарь по postId
            stats_list = data.get("response", [])
            return {stat["postId"]: stat for stat in stats_list}
    except Exception as e:
        print(f"Error getting detailed stats: {e}")

    return {}


async def _save_channel_snapshot(
    social_account: SocialAccount, channel_stats: dict
) -> ProfileSnapshot:
    """Сохранить снимок профиля канала"""
    snapshot = await ProfileSnapshot.create(
        social_account=social_account,
        snapshot_date=datetime.now(),
        followers_count=channel_stats.get("participants_count", 0),
        following_count=0,  # Telegram не показывает подписки
        total_likes=0,  # В Telegram нет лайков, есть реакции
        total_posts=channel_stats.get("posts_count", 0),
        avatar_url=channel_stats.get("image640", "").replace("//", "https://"),
        extra_data={
            "title": channel_stats.get("title"),
            "username": channel_stats.get("username"),
            "peer_type": channel_stats.get("peer_type"),
            "avg_post_reach": channel_stats.get("avg_post_reach", 0),
            "adv_post_reach_12h": channel_stats.get("adv_post_reach_12h", 0),
            "adv_post_reach_24h": channel_stats.get("adv_post_reach_24h", 0),
            "adv_post_reach_48h": channel_stats.get("adv_post_reach_48h", 0),
            "err_percent": channel_stats.get("err_percent", 0),
            "err24_percent": channel_stats.get("err24_percent", 0),
            "er_percent": channel_stats.get("er_percent", 0),
            "daily_reach": channel_stats.get("daily_reach", 0),
            "ci_index": channel_stats.get("ci_index", 0),
            "mentions_count": channel_stats.get("mentions_count", 0),
            "forwards_count": channel_stats.get("forwards_count", 0),
            "mentioning_channels_count": channel_stats.get(
                "mentioning_channels_count", 0
            ),
            "category": channel_stats.get("category"),
            "country": channel_stats.get("country"),
            "language": channel_stats.get("language"),
        },
    )

    return snapshot


async def _save_telegram_post(social_account: SocialAccount, post_data: dict) -> Video:
    """Сохранить или обновить пост Telegram"""
    post_id = str(post_data.get("id"))

    # Парсим дату публикации (timestamp)
    post_date = post_data.get("date")
    created_at_platform = (
        datetime.fromtimestamp(post_date) if post_date else datetime.now()
    )

    # Получаем статистику из детальных данных если есть
    detailed_stats = post_data.get("detailed_stats", {})

    # Получаем URL поста
    post_url = post_data.get("link", "")

    # Получаем текст поста
    text = post_data.get("text", "")

    # Получаем медиа информацию
    media = post_data.get("media", {})
    media_type = media.get("media_type") if media else None

    # Проверяем существование поста
    existing_post = await Video.filter(
        social_account=social_account, platform_video_id=post_id
    ).first()

    video_data_dict = {
        "social_account": social_account,
        "platform_video_id": post_id,
        "platform_author_id": str(
            post_data.get("channel_id", social_account.platform_user_id)
        ),
        "description": text,
        "created_at_platform": created_at_platform,
        "video_url": None,  # Telegram API не предоставляет прямые ссылки на медиа
        "share_url": post_url,
        "cover_url": None,
        "thumbnail_url": None,
        "duration_ms": None,
        "views_count": detailed_stats.get("viewsCount", post_data.get("views", 0)),
        "likes_count": detailed_stats.get("reactionsCount", 0),  # В Telegram - реакции
        "comments_count": detailed_stats.get("commentsCount", 0),
        "shares_count": detailed_stats.get("sharesCount", 0),
        "saves_count": 0,  # Telegram API не предоставляет сохранения
        "last_updated": datetime.now(),
        "extra_data": {
            "is_deleted": post_data.get("is_deleted", 0),
            "forwarded_from": post_data.get("forwarded_from"),
            "media_type": media_type,
            "mime_type": media.get("mime_type") if media else None,
            "media_size": media.get("size") if media else None,
        },
    }

    if existing_post:
        # Обновляем существующий пост
        for key, value in video_data_dict.items():
            if key != "social_account":
                setattr(existing_post, key, value)
        await existing_post.save()
        return existing_post
    else:
        # Создаем новый пост
        video = await Video.create(**video_data_dict)
        return video
