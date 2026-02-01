@echo off
echo === Инициализация TikTok Analytics Service ===

REM Проверка .env файла
if not exist .env (
    echo Создание .env файла из .env.example...
    copy .env.example .env
    echo.
    echo [ВАЖНО] Отредактируйте .env файл и укажите ваш SCRAPECREATORS_API_KEY
    pause
    exit /b 1
)

REM Запуск контейнеров
echo Запуск Docker контейнеров...
docker-compose up -d

REM Ожидание готовности базы данных
echo Ожидание готовности базы данных...
timeout /t 5 /nobreak > nul

echo.
echo [OK] Сервис запущен!
echo [INFO] API документация: http://localhost:8000/docs
echo [INFO] Health check: http://localhost:8000/health
echo.
echo Просмотр логов: docker-compose logs -f app
echo Остановка: docker-compose down
pause
