from django.contrib.auth.models import User
from django.db import models

from .constants import Position
from companies.models import Company


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    team = models.ForeignKey(Company, on_delete=models.SET_NULL,
                             related_name='profiles', verbose_name='Компания')
    position = models.CharField(max_length=32, choices=Position.choices,
                                default=Position.EMPLOYEE, verbose_name='Должность')
    is_administrator = models.BooleanField(default=False, verbose_name='Администратор?')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

