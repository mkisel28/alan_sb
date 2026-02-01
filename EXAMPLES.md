# Примеры использования API

Этот файл содержит примеры запросов к API сервиса.

## 1. Создание автора

```bash
curl -X POST "http://localhost:8000/api/authors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ксения Буглак"
  }'
```

Ответ:
```json
{
  "id": 1,
  "name": "Ксения Буглак",
  "created_at": "2026-01-21T10:00:00",
  "updated_at": "2026-01-21T10:00:00"
}
```

## 2. Получение списка авторов

```bash
curl "http://localhost:8000/api/authors"
```

## 3. Добавление TikTok аккаунта автору

```bash
curl -X POST "http://localhost:8000/api/social-accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": 1,
    "platform": "tiktok",
    "platform_user_id": "6868974846787077121",
    "username": "ksenia_buglak",
    "profile_url": "https://www.tiktok.com/@ksenia_buglak"
  }'
```

Ответ:
```json
{
  "id": 1,
  "author_id": 1,
  "platform": "tiktok",
  "platform_user_id": "6868974846787077121",
  "username": "ksenia_buglak",
  "profile_url": "https://www.tiktok.com/@ksenia_buglak",
  "is_active": true,
  "created_at": "2026-01-21T10:00:00",
  "updated_at": "2026-01-21T10:00:00"
}
```

## 4. Сбор данных из TikTok

```bash
curl -X POST "http://localhost:8000/api/collect/tiktok/1" \
  -H "Content-Type: application/json" \
  -d '{
    "max_videos": 50
  }'
```

Ответ:
```json
{
  "success": true,
  "message": "Successfully collected 50 videos",
  "videos_collected": 50,
  "profile_updated": true,
  "credits_remaining": 71
}
```

## 5. Получение видео аккаунта

```bash
curl "http://localhost:8000/api/collect/videos/1?limit=10&offset=0"
```

## 6. Получение истории снимков профиля

```bash
curl "http://localhost:8000/api/collect/profile-snapshots/1?limit=30"
```

## 7. Получение социальных сетей автора

```bash
curl "http://localhost:8000/api/social-accounts/authors/1"
```

## Python примеры

### Создание автора и добавление TikTok

```python
import requests

BASE_URL = "http://localhost:8000"

# Создать автора
response = requests.post(f"{BASE_URL}/api/authors", json={
    "name": "Ксения Буглак"
})
author = response.json()
print(f"Создан автор: {author}")

# Добавить TikTok аккаунт
response = requests.post(f"{BASE_URL}/api/social-accounts", json={
    "author_id": author["id"],
    "platform": "tiktok",
    "platform_user_id": "6868974846787077121",
    "username": "ksenia_buglak",
    "profile_url": "https://www.tiktok.com/@ksenia_buglak"
})
social_account = response.json()
print(f"Добавлен аккаунт: {social_account}")

# Собрать данные
response = requests.post(
    f"{BASE_URL}/api/collect/tiktok/{social_account['id']}", 
    json={"max_videos": 50}
)
result = response.json()
print(f"Результат сбора: {result}")

# Получить видео
response = requests.get(
    f"{BASE_URL}/api/collect/videos/{social_account['id']}",
    params={"limit": 10}
)
videos = response.json()
print(f"Получено видео: {len(videos)}")
for video in videos:
    print(f"  - {video['description'][:50]}... | Просмотры: {video['views_count']}")
```
