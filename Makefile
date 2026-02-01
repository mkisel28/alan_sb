.PHONY: help build up down logs shell db-shell test clean init

help:
	@echo "Доступные команды:"
	@echo "  make init        - Первоначальная инициализация проекта"
	@echo "  make build       - Собрать Docker образы"
	@echo "  make up          - Запустить сервисы"
	@echo "  make down        - Остановить сервисы"
	@echo "  make logs        - Просмотр логов"
	@echo "  make shell       - Войти в контейнер приложения"
	@echo "  make db-shell    - Войти в PostgreSQL"
	@echo "  make clean       - Очистить все (контейнеры, volumes)"

init:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Создан .env файл"; \
		echo "⚠️  Отредактируйте .env и укажите SCRAPECREATORS_API_KEY"; \
	else \
		echo ".env файл уже существует"; \
	fi

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Сервис запущен на http://localhost:8000"
	@echo "📝 Документация API: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app /bin/bash

db-shell:
	docker-compose exec db psql -U postgres -d analytics

clean:
	docker-compose down -v
	@echo "✅ Все контейнеры и volumes удалены"
