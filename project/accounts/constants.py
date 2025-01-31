from django.utils.translation import gettext_lazy as _
from django.db import models


class Position(models.TextChoices):
    EMPLOYEE = 'EMPLOYEE', _('Подчиненный')
    MANAGER = 'MANAGER', _('Менеджер')
    BOSS = 'BOSS', _('Генеральный Менеджер')
