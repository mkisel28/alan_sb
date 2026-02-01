from typing import List
from fastapi import APIRouter, HTTPException
from models import Author, SocialAccount, ProfileSnapshot, Video
from schemas import SocialAccountCreate, SocialAccountUpdate, SocialAccountResponse

router = APIRouter(prefix="/api/social-accounts", tags=["social-accounts"])


@router.post("", response_model=SocialAccountResponse)
async def create_social_account(social_account: SocialAccountCreate):
    """Добавить социальную сеть автору"""
    # Проверяем существование автора
    author = await Author.filter(id=social_account.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Проверяем, не существует ли уже такой аккаунт
    existing = await SocialAccount.filter(
        platform=social_account.platform,
        platform_user_id=social_account.platform_user_id,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Social account already exists")

    # Создаем новый аккаунт
    new_account = await SocialAccount.create(
        author_id=social_account.author_id,
        platform=social_account.platform,
        platform_user_id=social_account.platform_user_id,
        username=social_account.username,
        profile_url=social_account.profile_url,
    )

    return SocialAccountResponse.model_validate(new_account, from_attributes=True)


@router.get("/authors/{author_id}", response_model=List[SocialAccountResponse])
async def get_author_social_accounts(author_id: int):
    author = await Author.filter(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    accounts = await SocialAccount.filter(author_id=author_id).all()
    return [
        SocialAccountResponse.model_validate(acc, from_attributes=True)
        for acc in accounts
    ]


@router.get("/{account_id}", response_model=SocialAccountResponse)
async def get_social_account(account_id: int):
    """Получить социальный аккаунт по ID"""
    account = await SocialAccount.filter(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    return SocialAccountResponse.model_validate(account, from_attributes=True)


@router.put("/{account_id}", response_model=SocialAccountResponse)
async def update_social_account(account_id: int, account_data: SocialAccountUpdate):
    """Обновить социальный аккаунт"""
    account = await SocialAccount.filter(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")

    if account_data.username is not None:
        account.username = account_data.username
    if account_data.profile_url is not None:
        account.profile_url = account_data.profile_url
    if account_data.is_active is not None:
        account.is_active = account_data.is_active

    await account.save()
    return SocialAccountResponse.model_validate(account, from_attributes=True)


@router.delete("/{account_id}")
async def delete_social_account(account_id: int):
    """Удалить социальный аккаунт и все связанные данные"""
    account = await SocialAccount.filter(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")

    # Удаляем все видео
    await Video.filter(social_account_id=account_id).delete()

    # Удаляем все снапшоты профиля
    await ProfileSnapshot.filter(social_account_id=account_id).delete()

    # Удаляем аккаунт
    await account.delete()

    return {"success": True, "message": "Social account and all related data deleted"}
