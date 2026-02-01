from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgres://postgres:postgres@localhost:5432/analytics"

    # ScrapeCreators API
    scrapecreators_api_key: str
    scrapecreators_api_url: str = "https://api.scrapecreators.com"

    # TGStat API
    tgstat_api_token: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Tortoise ORM конфигурация
TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
