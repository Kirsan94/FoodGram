# Ссылка на тестовый проект

Проект тестово развернут на удаленном сервере, описание функционала API доступно по адресу http://130.193.40.178/redoc/ . Настроена возможность автоматического тестирования, размещения в DockerHub, деплоя и отправки оповещения через бота в Telegram. Реализовано при помощи GitHub Actions в репозитории.

# praktikum_new_diplom
Проект Foodgram это продуктовый помощник. В функционал входит создание рецептов из доступных ингредиентов, добавление тэгов для удобного поиска и возможность подписки на понравившихся авторов. Проект доступен для просмотра неавторизованным пользователям, после регистрации можно публиковать свои рецепты.

### requirements

Файл со списком необходимых модулей можно найти в /backend/requirements.txt

### Основные ресурсы api:

- USERS - Регистрация пользователей, добавление в избранное и корзину, выдача токенов.
- TAGS - Тэги для рецептов.
- RECIPES - Рецепты и возможные действия с ними.
- INGREDIENTS - Ингредиенты для рецептов.

### Примеры запросов:

#### Регистрация нового пользователя:
POST /api/users/ HTTP/1.1
Content-Type: application/json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}

#### Получение списка тэгов:
GET /api/users/ HTTP/1.1
Content-Type: application/json
[
  {
    "id": 0,
    "name": "Завтрак",
    "color": "#E26C2D",
    "slug": "breakfast"
  }
]

#### Добавление рецепта:
POST /api/recipes/ HTTP/1.1
Content-Type: application/json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}

#### Добавление в корзину:
PATCH /api/v1/users/{username}/ HTTP/1.1
Content-Type: application/json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}

#### Удаление из списка избранного:
DELETE /api/recipes/{id}/favorite/ HTTP/1.1

Более подробнее см в /redoc/

### Шаблон наполнения .env файла:

Файл .env описывает переменные окружения, текущей конфигурацией предполагается его расположение в /infra. Пример его заполнения:
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=Qwerty123 # пароль для подключения к БД(задать собственный)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=* # секретный ключ

### Как запустить проект в Docker:

Перейти в директорию /infra/

Выполнить docker-compose up

По завершении сборки выполнить следующий набор команд:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
Админская панель доступна по адресу http://localhost/admin

### Наполнение базы данными:

Команда для выгрузки дампа базы данных:
docker-compose exec web python manage.py dumpdata > dump.json 
Команда для загрузки данных в базу:
docker-compose exec web python manage.py loaddata dump.json

### Примеры запросов:

К проекту подключен модуль redoc, содержащий документацию по доступным эндпоинтам и примерам запросов. Адрес для redoc - [base]/api/docs/redoc.html.

### Авторы проекта:

- Команда Яндекс.Практикума - ревью и консультации
- Дмитрий Филимонов - Студент-разработчик