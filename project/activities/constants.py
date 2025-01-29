from django.utils.translation import gettext_lazy as _
from django.db import models


class TaskStatuses(models.TextChoices):
    PENDING = 'PENDING', _('Выполняется')
    DEFERRED = 'DEFERRED', _('Отложено')
    FINISHED = 'FINISHED', _('Выполнено')
