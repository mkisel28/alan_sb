from tortoise import fields
from tortoise.models import Model


class Author(Model):
    """Автор холдинга"""

    id = fields.IntField(pk=True)
    name = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "authors"


class SocialAccount(Model):
    """Аккаунт автора в социальной сети"""

    PLATFORM_TIKTOK = "tiktok"
    PLATFORM_INSTAGRAM = "instagram"
    PLATFORM_YOUTUBE = "youtube"
    PLATFORM_YOUTUBE_SHORTS = "youtube_shorts"
    PLATFORM_FACEBOOK = "facebook"
    PLATFORM_TWITTER = "twitter"
    PLATFORM_TELEGRAM = "telegram"
    PLATFORM_TIKTOK = "tiktok"

    PLATFORM_CHOICES = [
        (PLATFORM_TIKTOK, "TikTok"),
        (PLATFORM_INSTAGRAM, "Instagram"),
        (PLATFORM_YOUTUBE, "YouTube"),
        (PLATFORM_YOUTUBE_SHORTS, "YouTube Shorts"),
        (PLATFORM_FACEBOOK, "Facebook"),
        (PLATFORM_TWITTER, "Twitter/X"),
        (PLATFORM_TELEGRAM, "Telegram"),
    ]

    id = fields.IntField(pk=True)
    author = fields.ForeignKeyField("models.Author", related_name="social_accounts")
    platform = fields.TextField()  # tiktok, instagram, youtube и т.д.
    platform_user_id = fields.TextField()  # ID пользователя в платформе
    username = fields.TextField(null=True)  # Никнейм
    profile_url = fields.TextField(null=True)  # Ссылка на профиль
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "social_accounts"
        unique_together = [("platform", "platform_user_id")]


class ProfileSnapshot(Model):
    """Снимок профиля на определенную дату"""

    id = fields.IntField(pk=True)
    social_account = fields.ForeignKeyField(
        "models.SocialAccount", related_name="snapshots"
    )
    snapshot_date = fields.DatetimeField(auto_now_add=True)

    # Общие данные профиля
    followers_count = fields.IntField(default=0)
    following_count = fields.IntField(default=0, null=True)
    total_likes = fields.BigIntField(default=0, null=True)
    total_posts = fields.IntField(default=0, null=True)

    # Медиа
    avatar_url = fields.TextField(null=True)

    # Дополнительные данные (JSON)
    extra_data = fields.JSONField(default=dict)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "profile_snapshots"
        indexes = [("social_account", "snapshot_date")]


class Video(Model):
    """Видео/пост из социальной сети"""

    id = fields.IntField(pk=True)
    social_account = fields.ForeignKeyField(
        "models.SocialAccount", related_name="videos"
    )

    # Идентификаторы платформы
    platform_video_id = fields.CharField(max_length=1024, unique=True)
    platform_author_id = fields.TextField()

    # Основные данные
    description = fields.TextField(null=True)
    created_at_platform = fields.DatetimeField()  # Когда опубликовано в соцсети
    video_url = fields.TextField(null=True)
    share_url = fields.TextField(null=True)

    # Медиа
    cover_url = fields.TextField(null=True)  # Обложка/превью
    thumbnail_url = fields.TextField(null=True)

    # Характеристики видео
    duration_ms = fields.IntField(null=True)  # Длительность в миллисекундах

    # Метрики (текущие значения)
    views_count = fields.BigIntField(default=0)
    likes_count = fields.BigIntField(default=0)
    comments_count = fields.IntField(default=0)
    shares_count = fields.IntField(default=0)
    saves_count = fields.IntField(default=0, null=True)

    # Дополнительные данные
    extra_data = fields.JSONField(default=dict)

    # Служебные поля
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "videos"
        indexes = [
            ("social_account", "created_at_platform"),
            ("platform_video_id",),
        ]


class VideoMetricsHistory(Model):
    """История изменения метрик видео"""

    id = fields.IntField(pk=True)
    video = fields.ForeignKeyField("models.Video", related_name="metrics_history")

    snapshot_date = fields.DatetimeField(auto_now_add=True)

    views_count = fields.BigIntField(default=0)
    likes_count = fields.BigIntField(default=0)
    comments_count = fields.IntField(default=0)
    shares_count = fields.IntField(default=0)
    saves_count = fields.IntField(default=0, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "video_metrics_history"
        indexes = [("video", "snapshot_date")]
