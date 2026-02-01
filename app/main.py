from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from config import TORTOISE_ORM
from api.authors import router as authors_router
from api.social_accounts import router as social_accounts_router
from api.collect import router as collect_router
from api.analytics import router as analytics_router
from api.reports import router as reports_router


app = FastAPI(
    title="TikTok Analytics API",
    description="Сервис сбора данных авторов из TikTok",
    version="1.0.0",
)
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  #
    add_exception_handlers=True,
)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(authors_router)
app.include_router(social_accounts_router)
app.include_router(collect_router)
app.include_router(analytics_router)
app.include_router(reports_router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "TikTok Analytics API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {"status": "ok"}
