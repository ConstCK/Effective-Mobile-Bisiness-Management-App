from django.db import models

from accounts.models import Profile
from .constants import TaskStatuses


class News(models.Model):
    title = models.CharField(max_length=128, verbose_name='Заголовок новости')
    content = models.TextField(verbose_name='Содержание новости')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               verbose_name='Автор новости')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Task(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название задачи')
    assigned_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tasks',
                                    verbose_name='Создатель задачи')
    assigned_to = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tasks',
                                    verbose_name='Исполнитель задачи')
    created_at = models.DateTimeField(auto_add=True, verbose_name='Дата создания задачи')
    deadline = models.DateTimeField(verbose_name='Deadline задачи')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class TaskStatus(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Задача')
    status = models.CharField(max_length=16, choices=TaskStatuses.choices,
                              default=TaskStatuses.PENDING, verbose_name='Статус задачи')
    comment = models.CharField(max_length=128, blank=True, verbose_name='Комментарий к задаче')

    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        constraints = (models.UniqueConstraint(fields=('task', 'status'),
                                               name='Unique task constraint'))


class TaskEstimation(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, verbose_name='Задача')
    deadline_meeting = models.PositiveSmallIntegerField(verbose_name='Соблюдение сроков задачи')
    completeness = models.PositiveSmallIntegerField(verbose_name='Полнота выполнения задачи')
    quality = models.PositiveSmallIntegerField(verbose_name='Качество выполнения задачи')

    class Meta:
        verbose_name = 'Оценка задачи'
        verbose_name_plural = 'Оценки задач'


class Meeting(models.Model):
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                  related_name='meetings',
                                  verbose_name='Организатор встречи')
    start_at = models.DateTimeField(verbose_name='Время начала встречи')
    end_at = models.DateTimeField(verbose_name='Время завершения встречи')
    participants = models.ManyToManyField(Profile,
                                          verbose_name='Участники встречи')

    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'


class Calendar(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название дела', blank=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                              related_name='calendars',
                              verbose_name='Владелец зарезервированного времени')
    start_at = models.DateTimeField(verbose_name='Время начала дела')
    end_at = models.DateTimeField(verbose_name='Время окончания дела')

    class Meta:
        verbose_name = 'Зарезервированное время для дел'
        verbose_name_plural = 'Зарезервированное время для дел'
        constraints = (models.UniqueConstraint(fields=('owner', 'start_at', 'end_at'),
                                               name='Unique calendar constraint'))
