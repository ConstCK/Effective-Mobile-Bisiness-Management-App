from django.utils.translation import gettext_lazy as _
from django.db import models


class Position(models.TextChoices):
    EMPLOYEE = 'EMPLOYEE', _('Подчиненный')
    MANAGER = 'MANAGER', _('Менеджер')
    BOSS = 'BOSS', _('Генеральный Менеджер')


class TestProfileData:
    user_1 = {
        'username': 'Petrov',
        'password': 'user1234',
        'is_staff': 'True'
    }
    user_2 = {
        'username': 'Ivanov',
        'password': 'user1234',
        'is_staff': 'False'
    }
    user_3 = {
        'username': 'Volkov',
        'password': 'user1234',
        'is_staff': 'False'
    }
    user_4 = {
        'username': 'Gromov',
        'password': 'user1234',
        'is_staff': 'False'
    }

    user_fail = {
        'username': 'Gromov',
        'password': '123',
        'is_staff': 'False'
    }

    login_password = {
        'username': 'Petrov',
        'password': 'user1234'
    }

    new_structure = {'name': 'Линейно-Функциональная'}


