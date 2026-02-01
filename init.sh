#!/bin/bash

echo "=== Инициализация TikTok Analytics Service ==="

# Проверка .env файла
if [ ! -f .env ]; then
    echo "Создание .env файла из .env.example..."
    cp .env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и укажите ваш SCRAPECREATORS_API_KEY"
    exit 1
fi

# Запуск контейнеров
echo "Запуск Docker контейнеров..."
docker-compose up -d

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
sleep 5

echo ""
echo "✅ Сервис запущен!"
echo "📝 API документация: http://localhost:8000/docs"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "Просмотр логов: docker-compose logs -f app"
echo "Остановка: docker-compose down"
