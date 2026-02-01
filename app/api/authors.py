from typing import List
from fastapi import APIRouter, HTTPException
from models import Author, SocialAccount, ProfileSnapshot, Video
from schemas import AuthorCreate, AuthorUpdate, AuthorResponse

router = APIRouter(prefix="/api/authors", tags=["authors"])


@router.post("", response_model=AuthorResponse)
async def create_author(author: AuthorCreate):
    """Создать нового автора"""
    new_author = await Author.create(name=author.name)
    return AuthorResponse.model_validate(new_author, from_attributes=True)


@router.get("", response_model=List[AuthorResponse])
async def get_authors():
    """Получить список всех авторов"""
    authors = await Author.all()
    return [
        AuthorResponse.model_validate(author, from_attributes=True)
        for author in authors
    ]


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int):
    """Получить автора по ID"""
    author = await Author.filter(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return AuthorResponse.model_validate(author, from_attributes=True)


@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(author_id: int, author_data: AuthorUpdate):
    """Обновить автора"""
    author = await Author.filter(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = author_data.name
    await author.save()
    return AuthorResponse.model_validate(author, from_attributes=True)


@router.delete("/{author_id}")
async def delete_author(author_id: int):
    """Удалить автора и все связанные данные"""
    author = await Author.filter(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Получаем все социальные аккаунты автора
    social_accounts = await SocialAccount.filter(author_id=author_id).all()

    # Удаляем все связанные данные для каждого аккаунта
    for account in social_accounts:
        # Удаляем видео
        await Video.filter(social_account_id=account.id).delete()
        # Удаляем снапшоты профиля
        await ProfileSnapshot.filter(social_account_id=account.id).delete()

    # Удаляем социальные аккаунты
    await SocialAccount.filter(author_id=author_id).delete()

    # Удаляем автора
    await author.delete()

    return {"success": True, "message": "Author and all related data deleted"}
