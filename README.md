# Проект «RECIPEGRAM»

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)


"Фудграм" - сайт на котором пользователи публикуют свои рецепты. Могут добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Возможности проекта

Проект позволяет пользователям:

1. Записывать свои рецепты и делиться ими с другими пользоватями.
2. Просматривать рецепты других пользователей.
3. Систему подписок на пользователей (чтобы не пропустить новые их публицкации).
4. Добавлять рецепты в избранное.
5. Добавлять рецепты в список покупок.
6. Скачивать список покупок в формате .txt

## Установка проекта

1. Клонировать репозиторий из GitHub:
~~~
git clone https://github.com/dnaryshkin/recipegram.git
~~~
2. Для корректной работы в корне проекта необходимо создать `.env` заполненный по примеру файла `.env_example`.
~~~
USE_SQLITE=True_or_False # True для подключение базы данных Sqlite
SECRET_KEY='your_secret_key_project'  # установите свой секретный пароль проекта
DEBUG=True_or_False # включение или отключение дебаг режима
ALLOWED_HOSTS=your_domain   # необходимо указать свой домен
POSTGRES_DB=project_db
POSTGRES_USER=project_user
POSTGRES_PASSWORD=project_password
DB_HOST=db
DB_PORT=5432
~~~

3. В корневой папке проекта recipegram выполнить:

~~~
docker-compose up
~~~

После запуска всех контейнеров, необходимо:
Выполнить миграции:
~~~
docker-compose exec recipegram_backend python manage.py migrate
~~~
Осуществить импорт данных из фикстур с содержимым ингредиентов и тегов, выполнением команды:
~~~
docker-compose exec recipegram_backend python manage.py import_csv
~~~
Необходимо создать суперпользователя для работы с админ-панелью:
~~~
docker-compose exec recipegram_backend python manage.py createsuperuser
~~~

## Примеры запросов к API
1. Регистрация пользователя

`POST` запрос к `http://localhost:8000/api/users/`
~~~
{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов",
"password": "Qwerty123"
}
~~~
При успешном запросе будет вывод:
~~~
{
"email": "vpupkin@yandex.ru",
"id": 0,
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов"
}
~~~

2. Получение списка рецептов:
`GET` запрос к `http://localhost:8000/api/recipes/`

Вывод:
~~~
{
  "count": 123,
  "next": "http://recipegram.example.org/api/recipes/?page=4",
  "previous": "http://recipegram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://recipegram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://recipegram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
~~~

3. Создание рецепта
`POST` запрос к `http://localhost:8000/api/recipes/`
С содержимым:
~~~
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
~~~
При успешном запросе будет вывод:
~~~
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://recipegram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://recipegram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
~~~

Более подробно со всей спецификацией API можно ознакомится на `http://localhost:8000/redoc`
