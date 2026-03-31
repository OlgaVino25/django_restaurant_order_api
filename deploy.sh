set -e

echo "Обновляем код из репозитория..."
git pull origin main

echo "Проверяем наличие .env файла..."
if [ ! -f .env ]; then
    echo "Ошибка: файл .env не найден. Скопируйте .env.example и заполните его."
    exit 1
fi

echo "Останавливаем старые контейнеры..."
docker-compose -f docker-compose.prod.yml down

echo "Собираем и запускаем новые контейнеры..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "Применяем миграции..."
docker-compose -f docker-compose.prod.yml exec -T web python backend/manage.py migrate

echo "Собираем статику..."
docker-compose -f docker-compose.prod.yml exec -T web python backend/manage.py collectstatic --noinput

echo "Деплой завершён успешно!"