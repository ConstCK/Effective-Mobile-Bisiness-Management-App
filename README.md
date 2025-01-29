# Приложение для управления бизнесом.

Скопируйте проект к себе на ПК при помощи: git clone clone **_Path_**
Перейдите в папку проекта
В терминале создайте виртуальное окружение (например python -m venv venv) и
активируйте его (venv\scripts\activate)
Установите все зависимости при помощи pip install -r requirements.txt
Создайте файл .env в каталоге проекта и пропишите в нем настройки по примеру .env.example
Например ключ для Django можно сгенерировать в python консоли при помощи
"from django.core.management.utils import get_random_secret_key, get_random_secret_key()"
Запустите сервер из каталога проекта (project/python manage.py runserver)

EndPoints:
http://127.0.0.1:8000/docs - Документация endpoints в Swagger
http://127.0.0.1:8000/redoc - Альтернативная документация endpoints 
http://127.0.0.1:8000/api/business/docs - Документация endpoints в Swagger


