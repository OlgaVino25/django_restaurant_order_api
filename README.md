# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Сайт доступен по адресу:  
**https://burger.vinokurova-om.ru**

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)

Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Как собрать бэкенд

Скачайте код:

```sh
git clone https://github.com/devmanorg/star-burger.git
```

Перейдите в каталог проекта:

```sh
cd star-burger
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:

```sh
python --version
```

**Важно!** Версия Python должна быть не ниже 3.10.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

В каталоге проекта создайте виртуальное окружение:

```sh
python -m venv venv
```

Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

Установите зависимости в виртуальное окружение:

```sh
pip install -r requirements.txt
```

Определите переменную окружения `SECRET_KEY`. Создать файл `.env` в каталоге `star_burger/` и положите туда такой код:

```sh
YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекс_геокодера
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=django-insecure-0if40nf4nf93n4
DEBUG=True
```

Получение Yandex Geocoder API ключа:

Перейдите в [кабинете разработчика](https://developer.tech.yandex.ru/services)
Создайте новый ключ для Geocoder API
Скопируйте ключ в переменную `YANDEX_GEOCODER_API_KEY`

Создайте файл базы данных SQLite и отмигрируйте её следующей командой:

```sh
python manage.py migrate
```

Запустите сервер:

```sh
python manage.py runserver
```

После миграций создайте суперпользователя для доступа к админке:

```sh
python manage.py createsuperuser
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.

### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

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

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточны, и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.

## Настройка Rollbar для мониторинга ошибок

### Для разработки (локально):

1. Создайте аккаунт на [rollbar.com](https://rollbar.com)
2. Создайте новый проект типа "Django"
3. Получите `POST_SERVER_ITEM_ACCESS_TOKEN`
4. Добавьте в `.env`:

```bash
ROLLBAR_ACCESS_TOKEN=ваш_токен_здесь
ROLLBAR_ENVIRONMENT=development
```

## Установка PostgreSQL для разработки

Установите PostgreSQL и pgAdmin 4

1. Создайте базу данных и пользователя через pgAdmin:
   - Database: `star_burger`
   - User: `star_burger_user`

2. Примените миграции:

```powershell
python manage.py migrate
```

### Для продакшена (сервер):

1. На сервере в файле .env установите:

```bash
ROLLBAR_ACCESS_TOKEN=ваш_токен_здесь
ROLLBAR_ENVIRONMENT=production
DEBUG=False
```

2. Перезапустите сервис:

```bash
sudo systemctl restart star-burger-gunicorn
```

## Настройка PostgreSQL на сервере

1. Установите PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Создайте базу данных и пользователя:

```bash
sudo -u postgres psql
```

Выполните в psql:

```sql
CREATE DATABASE star_burger;
CREATE USER star_burger_user WITH PASSWORD 'сложный_пароль';
ALTER ROLE star_burger_user SET client_encoding TO 'utf8';
ALTER ROLE star_burger_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE star_burger_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE star_burger TO star_burger_user;
\q
```

3. Обновите `.env` файл на сервере:

```env
DATABASE_URL=postgres://star_burger_user:сложный_пароль@localhost:5432/star_burger
```

4. Примените миграции:

```bash
python manage.py migrate
```

5. Перенесите данные из старой базы (если нужно):

```bash
python manage.py dumpdata --indent 2 > data.json
python manage.py loaddata data.json
```

**Удалите SQLite файлы**

```bash
rm -f /opt/django_restaurant_order_api/db.sqlite3
```

## Как запустить prod-версию сайта

Собрать фронтенд:

```sh
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

## Переменные окружения

Проект использует следующие переменные окружения, которые необходимо настроить в файле `.env` в каталоге `star_burger/`:

### Обязательные переменные:

- `SECRET_KEY` — секретный ключ Django для шифрования данных (пароли, сессии, CSRF-токены). **Никогда не используйте значение по умолчанию в продакшене!**
- `ALLOWED_HOSTS` — список разрешенных хостов для работы Django. Например: `localhost,127.0.0.1,yourdomain.com`. [См. документацию Django](https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts)
- `DEBUG` — режим отладки. В разработке используйте `True`, в продакшене — `False`

- `ROLLBAR_ACCESS_TOKEN` - токен из Rollbar (обязательно)
- `ROLLBAR_ENVIRONMENT` - окружение: development или production (по умолчанию: development)

- `DATABASE_URL`=postgres://star*burger_user:ваш*пароль@localhost:5432/star_burger

### Переменные для геокодирования (обязательно для работы):

- `YANDEX_GEOCODER_API_KEY` — ключ API Яндекс.Геокодера для определения координат адресов доставки. Получить можно в [кабинете разработчика](https://developer.tech.yandex.ru/services)

### Переменные для безопасности (рекомендуются для продакшена):

- `CSRF_TRUSTED_ORIGINS` — список доверенных источников для CSRF-защиты, например: `https://yourdomain.com,https://www.yourdomain.com`
- `CSRF_COOKIE_SECURE` — установите `True`, чтобы куки CSRF передавались только по HTTPS
- `SESSION_COOKIE_SECURE` — установите `True`, чтобы сессионные куки передавались только по HTTPS

### Пример заполненного файла `.env` для разработки:

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

# База данных (если используете PostgreSQL)
DB_NAME=star_burger
DB_USER=star_burger_user
DB_PASSWORD=ваш_пароль
```

### Пример заполненного файла `.env` для продакшена (сервер):

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

1. Убедитесь, что установлены [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).
2. Клонируйте репозиторий и перейдите в папку проекта.
3. Создайте файл .env на основе .env.example и заполните его своими данными (ключи API, пароли и т.д.).
4. Запустите сборку и контейнеры:

```bash
docker-compose up --build
```

- Флаг `--build` пересоберёт образы при первом запуске или после изменений в `Dockerfile`.
- Фронтенд будет автоматически собираться в контейнере `frontend` и пересобираться при изменениях в папке `bundles-src`.

5. После успешного запуска откройте сайт по адресу http://localhost:8000.
6. Чтобы применить миграции (если они не применились автоматически) или создать суперпользователя, выполните в другом терминале:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Остановка: `Ctrl+C`, затем `docker-compose down`. Для полной очистки (включая тома с БД) используйте `docker-compose down -v`.

## Развёртывание на сервере с Docker

Проект полностью контейнеризирован. Для запуска на сервере потребуется только Docker и Docker Compose.

### Подготовка сервера

1. Установите Docker и Docker Compose:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

2. Клонируйте репозиторий на сервер
3. Создайте файл .env на основе .env.example и заполните его своими данными
4. Запустите скрипт деплоя (предварительно сделайте его исполняемым):

```bash
chmod +x deploy.sh
./deploy.sh
```

**Скрипт выполнит:**

- `git pull` для обновления кода.
- Остановку старых контейнеров.
- Пересборку и запуск новых контейнеров (`db` и `web`).
- Применение миграций и сборку статики.

## Настройка Nginx и SSL (на сервере, вне контейнера)

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

## Получение SSL-сертификата (Let's Encrypt)

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

## Обеспечение сохранности медиа-файлов

По умолчанию медиа-файлы хранятся в томе Docker. Чтобы они были доступны Nginx и не терялись при пересоздании контейнеров, скопируйте их на хост:

```bash
mkdir -p /opt/burger/media
docker cp burger-web-1:/app/media/. /opt/burger/media/
chmod -R 755 /opt/burger/media
```

После каждой загрузки новых картинок через админку повторяйте копирование. Альтернативно можно настроить bind mount в `docker-compose.prod.yml`, заменив том `media_volume:/app/media` на `./media:/app/media`.

## Финальная проверка

Откройте сайт по HTTPS: https://your-domain.com. Убедитесь, что:

- Статика (CSS, JS) загружается.
- Картинки товаров отображаются.
- Админка работает без ошибок CSRF.
- HTTP-запросы перенаправляются на HTTPS.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
