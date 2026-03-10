# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Сайт доступен по адресу:  
**https://burger.vinokurova-om.ru**

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)

Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта (без Docker)

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

1. Клонируйте репозиторий

2. Настройте бэкенд

Перейдите в папку `backend`:

```bash
cd backend
```

Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate        # для Linux/macOS
.\venv\Scripts\activate         # для Windows
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекс_геокодера
```

**Получение Yandex Geocoder API ключа:**

Перейдите в [кабинете разработчика](https://developer.tech.yandex.ru/services)
Создайте новый ключ для Geocoder API
Скопируйте ключ в переменную `YANDEX_GEOCODER_API_KEY`

Примените миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

Запустите сервер разработки:

```bash
python manage.py runserver
```

Сайт будет доступен по адресу http://127.0.0.1:8000, но пока без стилей и js, так как не собран фронтенд.

3. Соберите фронтенд (в отдельном терминале)

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет (рекомендуется версия 16):

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Вернитесь в корень проекта и перейдите в папку `frontend`:

```bash
cd ../frontend
```

Установите пакеты Node.js:

```bash
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```bash
npx parcel watch bundles-src/index.js --dist-dir bundles --public-url './'
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

После завершения сборки обновите страницу http://127.0.0.1:8000 – должен появиться полноценный интерфейс.

## Переменные окружения

Проект использует следующие переменные окружения, которые необходимо настроить в файле `.env`:

**Обязательные переменные:**

- `SECRET_KEY` — секретный ключ Django для шифрования данных (пароли, сессии, CSRF-токены). **Никогда не используйте значение по умолчанию в продакшене!**
- `ALLOWED_HOSTS` — список разрешенных хостов для работы Django. Например: `localhost,127.0.0.1,yourdomain.com`. [См. документацию Django](https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts)
- `DEBUG` — режим отладки. В разработке используйте `True`, в продакшене — `False`

- `ROLLBAR_ACCESS_TOKEN` - токен из Rollbar (опционально)
- `ROLLBAR_ENVIRONMENT` - окружение: development или production (по умолчанию: development) (опционально)

- `DATABASE_URL`=postgres://star_burger_user:ваш_пароль@localhost:5432/star_burger

**Переменные для геокодирования (обязательно для работы):**

- `YANDEX_GEOCODER_API_KEY` — ключ API Яндекс.Геокодера для определения координат адресов доставки. Получить можно в [кабинете разработчика](https://developer.tech.yandex.ru/services)

**Переменные для безопасности (рекомендуются для продакшена):**

- `CSRF_TRUSTED_ORIGINS` — список доверенных источников для CSRF-защиты, например: `https://yourdomain.com,https://www.yourdomain.com`
- `CSRF_COOKIE_SECURE` — установите `True`, чтобы куки CSRF передавались только по HTTPS
- `SESSION_COOKIE_SECURE` — установите `True`, чтобы сессионные куки передавались только по HTTPS

**Пример заполненного файла `.env` для разработки:**

```env
# Django
SECRET_KEY=ваш-секретный-ключ-здесь
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Яндекс.Геокодер
YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекс_геокодера

# Rollbar (опционально)
ROLLBAR_ACCESS_TOKEN=ваш_токен_здесь
ROLLBAR_ENVIRONMENT=production
```

**Пример заполненного файла `.env` для продакшена (сервер):**

```env
SECRET_KEY=ваш-секретный-ключ-здесь
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекс_геокодера

ROLLBAR_ACCESS_TOKEN=ваш_токен_здесь
ROLLBAR_ENVIRONMENT=production

DB_NAME=star_burger
DB_USER=star_burger_user
DB_PASSWORD=ваш_пароль

CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

## Запуск проекта в Docker (режим разработки)

Проект полностью контейнеризирован. Для разработки используется файл `docker-compose.yml`.

1. Убедитесь, что установлены [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).
2. Клонируйте репозиторий и перейдите в папку проекта.
3. Создайте файл `.env` на основе `.env.example` и заполните его своими данными (ключи API, пароли и т.д.).
4. Запустите сборку и контейнеры:

```bash
docker-compose up --build
```

- Флаг `--build` пересоберёт образы при первом запуске или после изменений в `Dockerfile`.
- Фронтенд будет автоматически собираться в контейнере `frontend` и пересобираться при изменениях в папке `frontend/bundles-src`.

5. После успешного запуска откройте сайт по адресу http://localhost:8000.
6. Чтобы применить миграции (если они не применились автоматически) или создать суперпользователя, выполните в другом терминале:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Остановка: `Ctrl+C`, затем `docker-compose down`. Для полной очистки (включая тома с БД) используйте `docker-compose down -v`.

## Развёртывание на сервере с Docker (production)

Проект полностью контейнеризирован. Для продакшена используется отдельный файл `docker-compose.prod.yml`, а в качестве веб-сервера выступает системный Nginx с SSL.

**Подготовка сервера:**

1. Установите Docker и Docker Compose:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

2. Клонируйте репозиторий на сервер в `/opt/burger`:

3. Создайте файл `.env` на основе `.env.example` и заполните его своими данными
4. Запустите скрипт деплоя (предварительно сделайте его исполняемым):

```bash
chmod +x deploy.sh
./deploy.sh
```

*Скрипт выполнит:*

- `git pull` для обновления кода.
- Остановку старых контейнеров.
- Пересборку и запуск новых контейнеров (`db` и `web`).
- Применение миграций и сборку статики.

**Настройка Nginx и SSL (на сервере, вне контейнера):**

1. Установите системный Nginx:

```bash
apt install nginx -y
```

2. Создайте конфигурацию для вашего домена:

```bash
nano /etc/nginx/sites-available/your-domain.com
```

3. Вставьте следующую конфигурацию (замените your-domain.com,www.your-domain.com на ваш домен):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location /static/ {
        alias /opt/burger/static/;
    }

    location /media/ {
        alias /opt/burger/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. Включите сайт и отключите стандартный:

```bash
ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default   # если есть
nginx -t
systemctl reload nginx
```

**Получение SSL-сертификата (Let's Encrypt):**

1. Установите Certbot:

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Следуйте инструкциям: введите email, согласитесь с условиями, выберите перенаправление с HTTP на HTTPS. Certbot автоматически обновит конфигурацию Nginx и настроит автообновление сертификата.

2. Проверьте автообновление:

```bash
systemctl status certbot.timer
certbot renew --dry-run
```

**Обеспечение сохранности медиа-файлов:**

По умолчанию медиа-файлы хранятся в томе Docker. Чтобы они были доступны Nginx и не терялись при пересоздании контейнеров, скопируйте их на хост:

```bash
mkdir -p /opt/burger/media
docker cp $(docker-compose -f docker-compose.prod.yml ps -q web):/app/media/. /opt/burger/media/
chmod -R 755 /opt/burger/media
```

После каждой загрузки новых картинок через админку повторяйте копирование. Альтернативно можно настроить bind mount в `docker-compose.prod.yml`, заменив том `media_volume:/app/media` на `./media:/app/media`.

## Финальная проверка

Откройте сайт по HTTPS: https://your-domain.com. Убедитесь, что:

- Статика (CSS, JS) загружается.
- Картинки товаров отображаются.
- Админка работает без ошибок CSRF.
- HTTP-запросы перенаправляются на HTTPS.

## Дополнительные настройки (опционально)

**Мониторинг ошибок с Rollbar:**

1. Зарегистрируйтесь на [rollbar.com](https://rollbar.com)
2. Создайте новый проект типа "Django"
3. Получите `POST_SERVER_ITEM_ACCESS_TOKEN`
4. Добавьте в `.env`:

```bash
ROLLBAR_ACCESS_TOKEN=ваш_токен_здесь
ROLLBAR_ENVIRONMENT=development
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
