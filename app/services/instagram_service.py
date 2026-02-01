"""
Сервис для сбора данных с Instagram через ScrapCreators API
"""

import httpx
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from models import SocialAccount, ProfileSnapshot, Video
from config import settings

SCRAPECREATORS_API_KEY = settings.scrapecreators_api_key
SCRAPECREATORS_BASE_URL = "https://api.scrapecreators.com"
MEDIA_ROOT = Path("/app/media")


async def _download_file(url: str, save_path: Path, retries: int = 3) -> bool:
    """Скачать файл по URL и сохранить локально"""
    # Создаем директорию если не существует
    save_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(response.content)

                return True
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
        ) as e:
            print(f"Попытка {attempt + 1}/{retries} - Ошибка скачивания {url}: {e}")
            if attempt == retries - 1:
                return False
        except Exception as e:
            print(f"Ошибка скачивания {url}: {e}")
            return False

    return False


async def collect_instagram_profile_data(
    social_account: SocialAccount,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Собрать данные профиля Instagram и посты за указанный период
    """
    if social_account.platform != "instagram":
        raise ValueError("Social account must be Instagram platform")

    # Устанавливаем значения по умолчанию для дат
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    handle = social_account.platform_user_id
    credits_used = 0
    posts_collected = 0
    profile_updated = False

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Получаем информацию о профиле
        profile_response = await client.get(
            f"{SCRAPECREATORS_BASE_URL}/v1/instagram/profile",
            params={"handle": handle},
            headers={"x-api-key": SCRAPECREATORS_API_KEY},
        )
        profile_response.raise_for_status()
        profile_data = profile_response.json()
        credits_used += 1

        # Сохраняем snapshot профиля
        if profile_data.get("success"):
            await _save_profile_snapshot(social_account, profile_data)
            profile_updated = True

            # Обновляем username если не задан
            user_data = profile_data.get("data", {}).get("user", {})
            if not social_account.username and user_data.get("username"):
                social_account.username = user_data["username"]
                await social_account.save()

        # 2. Собираем посты за указанный период
        posts_data = await _collect_posts(client, handle, start_date, end_date)
        credits_used += len(posts_data) // 50 + 1  # Примерная оценка

        # 3. Сохраняем посты
        for post_data in posts_data:
            await _save_instagram_post(social_account, post_data)
            posts_collected += 1

    return {
        "success": True,
        "message": f"Собрано {posts_collected} записей за период с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}",
        "posts_collected": posts_collected,
        "profile_updated": profile_updated,
        "credits_remaining": profile_data.get("credits_remaining"),
    }


async def _collect_posts(
    client: httpx.AsyncClient, handle: str, start_date: datetime, end_date: datetime
) -> list:
    """Собрать посты пользователя за указанный период"""
    all_posts = []
    next_max_id = None

    while True:
        params = {"handle": handle}
        if next_max_id:
            params["next_max_id"] = next_max_id

        response = await client.get(
            f"{SCRAPECREATORS_BASE_URL}/v2/instagram/user/posts",
            params=params,
            headers={"x-api-key": SCRAPECREATORS_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or not data.get("items"):
            break

        items = data["items"]

        # Фильтруем и проверяем даты
        for item in items:
            # Парсим дату публикации (device_timestamp в Unix времени)
            device_timestamp = item.get("device_timestamp")
            if device_timestamp:
                try:
                    post_date = datetime.fromtimestamp(device_timestamp)

                    # Проверяем диапазон дат
                    if post_date < start_date:
                        # Достигли начальной даты - прекращаем сбор
                        return all_posts

                    if post_date <= end_date:
                        all_posts.append(item)
                except (ValueError, OSError):
                    # Если не удалось распарсить дату, добавляем пост
                    all_posts.append(item)
            else:
                # Если нет временной метки, добавляем пост
                all_posts.append(item)

        # Проверяем наличие next_max_id для пагинации
        next_max_id = data.get("next_max_id")
        if not next_max_id or not data.get("more_available"):
            break

    return all_posts


async def _save_profile_snapshot(
    social_account: SocialAccount, profile_data: dict
) -> ProfileSnapshot:
    """Сохранить снимок профиля"""
    user_data = profile_data.get("data", {}).get("user", {})

    # Получаем URL аватара (HD версия если есть) и скачиваем
    avatar_url = None
    avatar_remote_url = user_data.get("profile_pic_url_hd") or user_data.get(
        "profile_pic_url"
    )

    if avatar_remote_url:
        # Сохраняем аватар локально
        user_id = social_account.platform_user_id
        avatar_dir = MEDIA_ROOT / "instagram" / user_id / "avatars"
        timestamp = int(datetime.now().timestamp())
        avatar_filename = f"{timestamp}.jpg"
        avatar_path = avatar_dir / avatar_filename

        if await _download_file(avatar_remote_url, avatar_path):
            avatar_url = f"/media/instagram/{user_id}/avatars/{avatar_filename}"

    # Получаем количество подписчиков и подписок
    followers_count = user_data.get("edge_followed_by", {}).get("count", 0)
    following_count = user_data.get("edge_follow", {}).get("count", 0)

    snapshot = await ProfileSnapshot.create(
        social_account=social_account,
        snapshot_date=datetime.now(),
        followers_count=followers_count,
        following_count=following_count,
        total_likes=0,  # Instagram API не предоставляет общее количество лайков
        total_posts=0,  # Можно посчитать из постов
        avatar_url=avatar_url,
        extra_data={
            "full_name": user_data.get("full_name"),
            "biography": user_data.get("biography"),
            "is_verified": user_data.get("is_verified", False),
            "is_private": user_data.get("is_private", False),
            "is_business_account": user_data.get("is_business_account", False),
            "category_name": user_data.get("category_name"),
        },
    )

    return snapshot


async def _save_instagram_post(social_account: SocialAccount, post_data: dict) -> Video:
    """Сохранить или обновить пост (видео/фото)"""
    post_id = post_data.get("id") or post_data.get("strong_id__")

    # Парсим дату публикации (используем device_timestamp в миллисекундах)
    device_timestamp = post_data.get("device_timestamp")
    if device_timestamp:
        # device_timestamp может быть в микросекундах (нужно разделить на 1000000)
        if device_timestamp > 10000000000000:  # Если больше, значит микросекунды
            timestamp_seconds = device_timestamp / 1000000
        else:
            timestamp_seconds = device_timestamp / 1000
        created_at_platform = datetime.fromtimestamp(timestamp_seconds)
    else:
        created_at_platform = datetime.now()

    # Получаем URL поста
    post_url = (
        post_data.get("url")
        or f"https://www.instagram.com/p/{post_data.get('code', '')}/"
    )

    # Получаем описание/подпись
    caption_data = post_data.get("caption", {})
    description = caption_data.get("text") if caption_data else None

    # Скачиваем обложку/изображение поста
    cover_url = None
    thumbnail_url = None

    # Пробуем получить URL изображения из разных источников
    cover_remote_url = post_data.get("display_uri")
    if not cover_remote_url and post_data.get("image_versions2", {}).get("candidates"):
        candidates = post_data["image_versions2"]["candidates"]
        if candidates:
            cover_remote_url = candidates[0].get("url")

    if cover_remote_url:
        # Сохраняем изображение локально
        user_id = social_account.platform_user_id
        posts_dir = MEDIA_ROOT / "instagram" / user_id / "posts"
        post_filename = f"{post_id}.jpg"
        post_path = posts_dir / post_filename

        if await _download_file(cover_remote_url, post_path):
            cover_url = f"/media/instagram/{user_id}/posts/{post_filename}"
            thumbnail_url = cover_url  # Используем то же изображение для thumbnail

    # Получаем видео URL если это видео
    video_url = None
    if post_data.get("video_versions"):
        video_versions = post_data["video_versions"]
        video_url = video_versions[0].get("url") if video_versions else None

    # Получаем длительность видео
    duration_ms = None
    video_duration = post_data.get("video_duration")
    if video_duration:
        duration_ms = int(video_duration * 1000)

    # Получаем метрики
    views_count = post_data.get("play_count", 0) or post_data.get("ig_play_count", 0)
    likes_count = post_data.get("like_count", 0)
    comments_count = post_data.get("comment_count", 0)

    # Проверяем существование поста
    existing_post = await Video.filter(
        social_account=social_account, platform_video_id=post_id
    ).first()

    video_data_dict = {
        "social_account": social_account,
        "platform_video_id": post_id,
        "platform_author_id": social_account.platform_user_id,
        "description": description,
        "created_at_platform": created_at_platform,
        "video_url": video_url,
        "share_url": post_url,
        "cover_url": cover_url,
        "thumbnail_url": thumbnail_url or cover_url,
        "duration_ms": duration_ms,
        "views_count": views_count,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "shares_count": 0,  # Instagram API не предоставляет количество репостов
        "saves_count": 0,  # Instagram API не предоставляет количество сохранений
        "last_updated": datetime.now(),
        "extra_data": {
            "has_audio": post_data.get("has_audio", False),
            "is_unified_video": post_data.get("is_unified_video", False),
            "filter_type": post_data.get("filter_type"),
            "original_width": post_data.get("original_width"),
            "original_height": post_data.get("original_height"),
        },
    }

    if existing_post:
        # Обновляем существующий пост
        for key, value in video_data_dict.items():
            if key != "social_account":  # Не обновляем foreign key
                setattr(existing_post, key, value)
        await existing_post.save()
        return existing_post
    else:
        # Создаем новый пост
        video = await Video.create(**video_data_dict)
        return video
