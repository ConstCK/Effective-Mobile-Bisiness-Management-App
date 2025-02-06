# Приложение для управления бизнесом.

* Скопируйте проект к себе на ПК при помощи: git clone clone https://github.com/ConstCK/Effective-Mobile-Bisiness-Management-App.git
* Перейдите в папку проекта
* В терминале создайте виртуальное окружение (например python -m venv venv) и
* активируйте его (venv\scripts\activate)
* Установите все зависимости при помощи pip install -r requirements.txt
* Создайте файл .env в каталоге проекта и пропишите в нем настройки по примеру .env.example
* Например, ключ для Django можно сгенерировать в python консоли при помощи
* "from django.core.management.utils import get_random_secret_key, get_random_secret_key()"
* Запустите сервер из каталога проекта (python manage.py runserver)

## Для запуска приложение в контейнере:

**Docker Desktop должен быть запущен
Команда запуска из директории проекта из консоли: docker-compose up**


## EndPoints:
### Подробности маршрутов в документации:
* localhost:8000/api/schema/swagger-ui/ - Документация endpoints в Swagger
* localhost:8000/api/schema/redoc/ - Альтернативная документация endpoints 
* localhost:8080/ - Администрирование БД в контейнере





