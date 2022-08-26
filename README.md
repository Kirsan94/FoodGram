![example workflow](https://github.com/kirsan94/FoodGram/actions/workflows/foodgram_workflow.yml/badge.svg)

## Дипломный проект FoodGram
Технологии:
 - Python
 - Django
 - Django REST Framework
 - Swagger
 - Docker
 - Nginx
 - React
 - PostgreSQL

Требуемые пакеты устанавливаются из ./backend/backend/requirements.txt

Проект FoodGram является площадкой для публикации рецептов блюд пользователей.
Доступен по адресу lirsan.sytes.net

Функционал включает в себя:

- Создание и редактирование рецептов из списка доступных ингредиентов
- Разметка рецептов по тэгам "Завтрак", "Обед" и "Ужин"
- Прикрепление изображения к рецептам (предполагается фото готового блюда)
- Описание метода приготовления с указанием времени
- Подписка на других пользователей - авторов рецептов
- Добавление рецептов в избранное
- Добавление рецептов в список покупок - в нём суммированы все ингредиенты добавленных в список рецептов
- Выгрузка списка покупок в файл .txt
- Поиск и фильтрация по различным параметрам
- Регистрация и авторизация пользователей

Проект доступен для просмотра всем пользхователям, однако для создания и добавления рецептов в избранное/список покупок необходимо авторизоваться. 

Проект поддерживает обращения к API, специализации находятся по адресу /api/docs/

---
### Запуск проекта
- Клонировать репозиторий
```
git clone git@github.com:Kirsan94/FoodGram.git
```
- Установить docker и docker-compose
```
sudo apt upgrade
sudo apt install docker.io 
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Убедиться в корректности заполнения файла .env

В данном проекте .env находится в ./infra/ и заполняется автоматически через workflow ./.github/workflows/yamdb_workflow.yml. Переменные задаются в secrets репозитория.
Пример заполнения .env можно увидеть в файле ./infra/example.env

- Провести миграции, запустить проект и импортировать базу

В данном проекте запуск, миграции и импорт в базу стартовых данных реилизованы через workflow ./.github/workflows/yamdb_workflow.yml - при ручном развёртывании команды можно взять оттуда.
При необходимости можно изменить используемый DockerHub образ в задачах build_and_push_to_docker_hub и deploy.

---
### Пользовательские роли
- Гость — может зарегистрироваться, просматривать рецепты на главной странице, просматривать отдельные страницы рецептов, просматривать страницы пользователей, фильтровать рецепты по тегам.

- Аутентифицированный пользователь — может использовать авторизацию, создавать/редактировать/удалять собственные рецепты, работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов, работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок, подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

- Администратор (admin) — полные права на управление всем контентом проекта.

### Регистрация нового пользователя
2. Права доступа: Доступно без токена.
4. Поля email и username должны быть уникальными.
---
### Примеры запросов к API:

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
GET /api/tags/ HTTP/1.1
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
      "id": 1,
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
POST /api/recipes/1/shopping_cart/ HTTP/1.1
Content-Type: application/json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}

#### Удаление из списка избранного:
DELETE /api/recipes/{id}/favorite/ HTTP/1.1

Более подробнее см. в /api/docs/

Разработчики:
- [Лев Харьков](https://github.com/Kirsan94)