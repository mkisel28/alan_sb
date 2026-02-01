from datetime import datetime
from pydantic import BaseModel


# Author schemas
class AuthorCreate(BaseModel):
    name: str


class AuthorUpdate(BaseModel):
    name: str


class AuthorResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# SocialAccount schemas
class SocialAccountCreate(BaseModel):
    author_id: int
    platform: str
    platform_user_id: str
    username: str | None = None
    profile_url: str | None = None


class SocialAccountUpdate(BaseModel):
    username: str | None = None
    profile_url: str | None = None
    is_active: bool | None = None


class SocialAccountResponse(BaseModel):
    id: int
    author_id: int
    platform: str
    platform_user_id: str
    username: str | None
    profile_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ProfileSnapshot schemas
class ProfileSnapshotResponse(BaseModel):
    id: int
    social_account_id: int
    snapshot_date: datetime
    followers_count: int
    following_count: int | None
    total_likes: int | None
    total_posts: int | None
    avatar_url: str | None

    class Config:
        from_attributes = True


# Video schemas
class VideoResponse(BaseModel):
    id: int
    social_account_id: int
    platform_video_id: str
    platform_author_id: str
    description: str | None
    created_at_platform: datetime
    video_url: str | None
    share_url: str | None
    cover_url: str | None
    thumbnail_url: str | None
    duration_ms: int | None
    views_count: int
    likes_count: int
    comments_count: int
    shares_count: int
    saves_count: int | None
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Collection schemas
class CollectTikTokRequest(BaseModel):
    max_videos: int | None = 100  


class CollectTikTokResponse(BaseModel):
    success: bool
    message: str
    videos_collected: int
    profile_updated: bool
    credits_remaining: int | None = None


# Analytics schemas
class SocialAccountAnalyticsResponse(BaseModel):
    social_account_id: int
    platform: str
    current_period: dict
    previous_period: dict | None = None
    comparison: dict | None = None

    class Config:
        from_attributes = True
