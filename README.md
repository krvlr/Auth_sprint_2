# Проектная работа 7 спринта
---

https://github.com/krvlr/Auth_sprint_2

В рамках данного репозитория реализованы следующие сервисы:

- Сервис авторизации

В рамках сервиса авторизации реализованы следующие `endpoint`-ы:

- `/api/v1/signup` - регистрация пользователя,
- `/api/v1/signin` - вход в аккаунт,
- `/api/v1/refresh` - получение свежего `Acccess` токена аутентифицированным пользователем (при наличии свежего и неиспользованного `Refresh` токена),
- `/api/v1/password/change` - изменение пароля аутентифицированного пользователя,
- `/api/v1/signout` - выход из устройства аутентифицированным пользователем (при наличии свежего `Acccess` токена),
- `/api/v1/signout/all` - выход из устройства аутентифицированным пользователем (при наличии свежего `Acccess` токена).
- `/api/v1/history` - получение списка действий текущего аутентифицированного пользователя (при наличии свежего `Acccess` токена).

В рамках онлайн-кинотеатра предусмотрена система подписок. 
Cервис авторизации предоставляет возможность аутентифицировать и авторизовать клиента с помощью активного `Access` токена.  
Для этого, в `payload` токена зашиты: 
- Права и роль пользователя, 
- Дополнительная информация.

При наличии секретного ключа, необходимого для проверки подписи активного `Access`-токена, каждый из микросервисов онлайн-кинотеатра сможет аутентифицировать и авторизовать пользователя.

При регистрации пользователь получает роль `пользователя` (`is_admin = False`), а также стандартные права, которые выдаются зарегистрированному пользователю по дефолту.

Администраторов сервиса авторизации необходимо добавлять в базу ручками (например администраторами сервиса авторизации). 

## Описание структуры репозитория:
---

1. `db` — раздел с настройками базы `PostgreSQL`.
2. `flask-auth` — раздел с описанием сервиса авторизации.
3. `nginx` — раздел с описанием настроек `nginx` для сервиса авторизации.

## Пример запуска
---

Перед запуском контейнеров, в корне `/` необходимо создать файл `.env` (в качестве примера `.env.example`):

    touch .env

А также указать в нем значения следующих переменных окружения:

    AUTH_DB_HOST
    AUTH_DB_PORT
    AUTH_DB_NAME
    AUTH_DB_USER
    AUTH_DB_PASSWORD
    AUTH_REDIS_HOST
    AUTH_REDIS_PORT
    JWT_COOKIE_SECURE
    JWT_TOKEN_LOCATION
    JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES
    INITIAL_USER_ROLES
    INITIAL_USER_DESCRIPTION_ROLES
    DEFAULT_USER_ROLE
    LOGGING_LEVEL
    LOG_FORMAT

Теперь можно запустить сборку образа и запуск контейнеров:

    docker compose up -d --build

Чтобы остановить и полностью удалить контейнеры со всеми `volume` и `network`, описанными в рамках `docker-compose.yml`:

    docker-compose down --rmi all -v --remove-orphans

## Миграции
---

Первым шагом необходимо перейти в дирректорию c точкой входа (`main.py`):

    cd /flask-auth/src/

Для генерации миграций структуры таблиц, описание которых находится в дирректории `/flask-auth/src/db/models` необходимо выполнить следующую команду:
    
    flask --app main db migrate -m "Описание миграции"

Для применения сформированной миграции необхожимо выполнить следующую команду:
    
    flask --app main db upgrade

## Тестирование
---

Для запуска тестирования необходимо перейти в папку с тестами:

    cd flask-auth/tests/functional/

создать файл `.env` (в качестве примера `flask-auth/tests/functional/.env.example`):

    touch .env

указать в нем значения тех же переменных окружения, что и для основного `docker-compose`,
создать файл `.env.tests` (в качестве примера `flask-auth/tests/functional/.env.tests.example`):

    touch .env.tests

указать в нем значения следующих переменных окружения:

    AUTH_DB_HOST
    AUTH_DB_PORT
    AUTH_DB_NAME
    AUTH_DB_USER
    AUTH_DB_PASSWORD
    AUTH_DB_TABLES
    AUTH_REDIS_HOST
    AUTH_REDIS_PORT
    AUTH_API_HOST
    AUTH_API_PORT
    AUTH_API_URI
    AUTH_API_PROTOCOL

И запустить сборку образа и запуск контейнеров для тестирования:

    docker compose up --build

Если в логах будет сообщение об успешном прохождении тестирования - значит пришел успех!

## Настройка flake8 и pre-commit hook
---

Сформируем виртуальное `Python`-окружение в корне:

    python3 -m venv env

Активируем сформированное виртуальное `Python`-окружение:

    . env/bin/activate

Обновим `pip`:

    pip install --upgrade pip

Установим зависимости проекта:

    pip install -r requirements.txt

Установим `pre-commit hook`:

    pre-commit install

## Пример использования реализованных `endpoint`-ов:
---

Импорт необходимых библиотек:

    import requests
    import json

### Регистрация /api/v1/signup

    data = {
        'login': 'ba',
        'password': '12345678',
        'email': 'test@yandex.ru'
    }
    port = 80

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/signup',
        json=data
    )
    
    print(response, json.loads(response.text))

### Вход /api/v1/signin

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/signin',
        json=data
    )
    
    print(response, json.loads(response.text))

    result = response.cookies.get_dict()

### Обновление access токена /api/v1/refresh

    refresh_cookies = {
        "refresh_token_cookie": result["refresh_token_cookie"],
    }

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/refresh',
        cookies=refresh_cookies,
    )

    print(response, json.loads(response.text))

### Выход из устройства /api/v1/signout

    headers = {
        "Authorization": f"Bearer {result['access_token_cookie']}",
    }

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/signout',
        headers=headers,
        json={
            'refresh_token': result['refresh_token_cookie'],
        }
    )

    print(response, json.loads(response.text))

### Выход со всех устройств /api/v1/signout/all

    headers = {
        "Authorization": f"Bearer {result['access_token_cookie']}",
    }

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/signout/all',
        headers=headers,
    )

    print(response, json.loads(response.text))

### Смена пароля /api/v1/password/change

    headers = {
        "Authorization": f"Bearer {result['access_token_cookie']}",
    }

    response = requests.post(
        url=f'http://127.0.0.1:{port}/api/v1/password/change',
        headers=headers,
        json={
            'old_password': '123456',
            'new_password': '12345678'
        }
    )

    response, json.loads(response.text)

### История действий пользователя /api/v1/history

    headers = {
        "Authorization": f"Bearer {result['access_token_cookie']}",
    }

    response = requests.get(
        url=f'http://127.0.0.1:{port}/api/v1/history',
        headers=headers,
    )

    print(response, json.loads(response.text))

## CI-CD
---

TBD: В `GitHub actions` настроен запуск линтера и тестов при событии `push`.
