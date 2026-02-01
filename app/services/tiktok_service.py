from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import httpx
import aiofiles
from config import settings
from models import SocialAccount, ProfileSnapshot, Video, VideoMetricsHistory


class TikTokService:
    """Сервис для работы с TikTok API через ScrapeCreators"""

    def __init__(self):
        self.api_key = settings.scrapecreators_api_key
        self.base_url = settings.scrapecreators_api_url
        self.headers = {"x-api-key": self.api_key}
        self.media_root = Path("/app/media")

    async def get_profile_videos(
        self, user_id: str, max_cursor: int | None = None
    ) -> Dict[str, Any]:
        """
        Получить видео профиля TikTok

        Args:
            user_id: ID пользователя TikTok
            max_cursor: Курсор для пагинации

        Returns:
            Ответ API с видео
        """
        url = f"{self.base_url}/v3/tiktok/profile/videos"
        params = {"user_id": user_id, "sort_by": "latest"}

        if max_cursor:
            params["max_cursor"] = max_cursor

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def collect_videos(
        self,
        social_account: SocialAccount,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Собрать записи TikTok профиля за указанный период

        Args:
            social_account: Аккаунт социальной сети
            start_date: Дата начала периода (по умолчанию - 30 дней назад)
            end_date: Дата окончания периода (по умолчанию - сегодня)

        Returns:
            Статистика сбора
        """
        print(end_date)
        # Устанавливаем дефолтные даты если не указаны
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        collected_posts = 0
        max_cursor = None
        credits_remaining = None
        profile_updated = False

        while True:
            # Получаем данные из API
            data = await self.get_profile_videos(
                user_id=social_account.platform_user_id, max_cursor=max_cursor
            )

            if not data.get("success"):
                break

            credits_remaining = data.get("credits_remaining")
            aweme_list = data.get("aweme_list", [])

            if not aweme_list:
                break

            # Обновляем данные профиля (из первого видео)
            if not profile_updated and aweme_list:
                await self._save_profile_snapshot(social_account, aweme_list[0])
                profile_updated = True

            # Сохраняем записи
            posts_in_batch = 0
            for aweme in aweme_list:
                # Получаем дату создания записи
                create_time = aweme.get("create_time")
                if create_time:
                    post_date = datetime.fromtimestamp(create_time)

                    # Проверяем, входит ли запись в диапазон дат
                    if post_date < start_date:
                        # Достигли начальной даты - прекращаем сбор
                        break

                    if post_date <= end_date:
                        await self._save_video(social_account, aweme)
                        collected_posts += 1
                        posts_in_batch += 1

            # Если в батче не было постов в диапазоне, останавливаемся
            if posts_in_batch == 0 and aweme_list:
                # Проверяем последний пост
                last_post = aweme_list[-1]
                last_create_time = last_post.get("create_time")
                if last_create_time:
                    last_post_date = datetime.fromtimestamp(last_create_time)
                    if last_post_date < start_date:
                        break

            # Проверяем, есть ли еще данные
            has_more = data.get("has_more", 0)
            if not has_more:
                break

            max_cursor = data.get("max_cursor")
            if not max_cursor:
                break

        return {
            "success": True,
            "message": f"Собрано {collected_posts} записей за период с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}",
            "posts_collected": collected_posts,
            "profile_updated": profile_updated,
            "credits_remaining": credits_remaining,
        }

    def _select_best_image_url(self, url_list: list) -> str | None:
        """Выбрать лучший URL изображения (предпочитаем .jpeg/.jpg вместо .heic)"""
        if not url_list:
            return None

        # Ищем URL с .jpeg или .jpg
        for url in url_list:
            if ".jpeg" in url.lower() or ".jpg" in url.lower():
                return url

        # Если не нашли, берем первый
        return url_list[0]

    async def _download_file(self, url: str, save_path: Path, retries: int = 3) -> bool:
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

    async def _save_profile_snapshot(
        self, social_account: SocialAccount, aweme: Dict[str, Any]
    ):
        """Сохранить снимок профиля"""
        author_data = aweme.get("author", {})

        # Извлекаем и скачиваем аватар
        avatar_url = None
        avatar_larger = author_data.get("avatar_larger", {})
        if avatar_larger and "url_list" in avatar_larger:
            url_list = avatar_larger["url_list"]
            if url_list:
                remote_url = url_list[0]
                # Сохраняем аватар
                user_dir = (
                    self.media_root
                    / "tiktok"
                    / social_account.platform_user_id
                    / "avatars"
                )
                timestamp = int(datetime.now().timestamp())
                avatar_filename = f"{timestamp}.jpg"
                avatar_path = user_dir / avatar_filename

                if await self._download_file(remote_url, avatar_path):
                    avatar_url = f"/media/tiktok/{social_account.platform_user_id}/avatars/{avatar_filename}"

        # Обновляем username и profile_url в social_account
        if author_data.get("unique_id"):
            social_account.username = author_data["unique_id"]
            social_account.profile_url = (
                f"https://www.tiktok.com/@{author_data['unique_id']}"
            )
            await social_account.save()

        # Создаем snapshot
        await ProfileSnapshot.create(
            social_account=social_account,
            followers_count=author_data.get("follower_count", 0),
            following_count=author_data.get("following_count", 0),
            total_likes=author_data.get("total_favorited", 0),
            total_posts=author_data.get("aweme_count", 0),
            avatar_url=avatar_url,
            extra_data=author_data,
        )

    async def _save_video(self, social_account: SocialAccount, aweme: Dict[str, Any]):
        """Сохранить или обновить видео"""
        video_id = aweme.get("aweme_id")
        if not video_id:
            return

        author_data = aweme.get("author", {})
        video_data = aweme.get("video", {})
        statistics = aweme.get("statistics", {})

        # Получаем и скачиваем обложку
        cover_url = None
        cover = video_data.get("cover", {})
        if cover and "url_list" in cover:
            url_list = cover["url_list"]
            if url_list:
                remote_url = self._select_best_image_url(url_list)
                if remote_url:
                    user_dir = (
                        self.media_root
                        / "tiktok"
                        / social_account.platform_user_id
                        / "covers"
                    )
                    cover_filename = f"{video_id}.jpg"
                    cover_path = user_dir / cover_filename

                    if await self._download_file(remote_url, cover_path):
                        cover_url = f"/media/tiktok/{social_account.platform_user_id}/covers/{cover_filename}"

        # Получаем и скачиваем превью (origin_cover)
        thumbnail_url = None
        origin_cover = video_data.get("origin_cover", {})
        if origin_cover and "url_list" in origin_cover:
            url_list = origin_cover["url_list"]
            if url_list:
                remote_url = self._select_best_image_url(url_list)
                if remote_url:
                    user_dir = (
                        self.media_root
                        / "tiktok"
                        / social_account.platform_user_id
                        / "thumbnails"
                    )
                    thumbnail_filename = f"{video_id}.jpg"
                    thumbnail_path = user_dir / thumbnail_filename

                    if await self._download_file(remote_url, thumbnail_path):
                        thumbnail_url = f"/media/tiktok/{social_account.platform_user_id}/thumbnails/{thumbnail_filename}"

        # Получаем URL видео
        video_url = None
        play_addr = video_data.get("play_addr", {})
        if play_addr and "url_list" in play_addr:
            url_list = play_addr["url_list"]
            if url_list:
                video_url = url_list[0]

        # Получаем дату создания
        create_time = aweme.get("create_time")
        if create_time:
            created_at_platform = datetime.fromtimestamp(create_time)
        else:
            created_at_platform = datetime.now()

        # Используем get_or_create для избежания конфликтов
        video, created = await Video.get_or_create(
            platform_video_id=video_id,
            defaults={
                "social_account_id": social_account.id,
                "platform_author_id": str(author_data.get("uid", "")),
                "description": aweme.get("desc"),
                "created_at_platform": created_at_platform,
                "video_url": video_url,
                "share_url": aweme.get("share_url"),
                "cover_url": cover_url,
                "thumbnail_url": thumbnail_url,
                "duration_ms": video_data.get("duration"),
                "views_count": statistics.get("play_count", 0),
                "likes_count": statistics.get("digg_count", 0),
                "comments_count": statistics.get("comment_count", 0),
                "shares_count": statistics.get("share_count", 0),
                "saves_count": statistics.get("collect_count", 0),
                "extra_data": aweme,
            },
        )

        # Если видео уже существовало, обновляем его
        if not created:
            video.social_account_id = social_account.id
            video.platform_author_id = str(author_data.get("uid", ""))
            video.description = aweme.get("desc")
            video.video_url = video_url
            video.share_url = aweme.get("share_url")
            video.cover_url = cover_url
            video.thumbnail_url = thumbnail_url
            video.duration_ms = video_data.get("duration")
            video.views_count = statistics.get("play_count", 0)
            video.likes_count = statistics.get("digg_count", 0)
            video.comments_count = statistics.get("comment_count", 0)
            video.shares_count = statistics.get("share_count", 0)
            video.saves_count = statistics.get("collect_count", 0)
            video.extra_data = aweme
            await video.save()

        # Сохраняем историю метрик
        await VideoMetricsHistory.create(
            video=video,
            views_count=statistics.get("play_count", 0),
            likes_count=statistics.get("digg_count", 0),
            comments_count=statistics.get("comment_count", 0),
            shares_count=statistics.get("share_count", 0),
            saves_count=statistics.get("collect_count", 0),
        )
