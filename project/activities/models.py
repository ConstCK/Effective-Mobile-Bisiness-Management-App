from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import Profile
from .constants import TaskStatuses


class News(models.Model):
    """
    Таблица созданных новостей
    """
    title = models.CharField(max_length=128, verbose_name='Заголовок новости')
    content = models.TextField(verbose_name='Содержание новости')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               verbose_name='Автор новости')

    def __str__(self) -> str:
        return f'Новость {self.title}'

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Task(models.Model):
    """
    Таблица назначенных задач
    """
    name = models.CharField(max_length=128, verbose_name='Название задачи')
    assigned_by = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                    related_name='created_task',
                                    verbose_name='Создатель задачи')
    assigned_to = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                    related_name='assigned_tasks',
                                    verbose_name='Исполнитель задачи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания задачи')
    deadline = models.DateTimeField(verbose_name='Deadline задачи')

    def __str__(self) -> str:
        return f'Задача {self.name}'

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        constraints = (models.UniqueConstraint(fields=('name', 'assigned_to'),
                                               name='Unique task constraint'),)


class TaskStatus(models.Model):
    """
    Таблица статусов выполнения задач
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Задача')
    status = models.CharField(max_length=16, choices=TaskStatuses.choices,
                              default=TaskStatuses.PENDING, verbose_name='Статус задачи')
    comment = models.CharField(max_length=128, blank=True, verbose_name='Комментарий к задаче')

    def __str__(self) -> str:
        return f'Статус задачи {self.task}'

    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        constraints = (models.UniqueConstraint(fields=('task', 'status'),
                                               name='Unique task status constraint'),)


class TaskEstimation(models.Model):
    """
    Таблица оценок выполнения задач
    """
    task = models.OneToOneField(Task, on_delete=models.CASCADE, verbose_name='Задача')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата выставления оценки',
                                      )
    deadline_meeting = models.PositiveSmallIntegerField(verbose_name='Соблюдение сроков задачи',
                                                        validators=(MaxValueValidator(10),
                                                                    MinValueValidator(1)))
    completeness = models.PositiveSmallIntegerField(verbose_name='Полнота выполнения задачи',
                                                    validators=(MaxValueValidator(10),
                                                                MinValueValidator(1))
                                                    )
    quality = models.PositiveSmallIntegerField(verbose_name='Качество выполнения задачи',
                                               validators=(MaxValueValidator(10),
                                                           MinValueValidator(1))
                                               )

    def __str__(self) -> str:
        return f'Оценка задачи {self.task}'

    class Meta:
        verbose_name = 'Оценка задачи'
        verbose_name_plural = 'Оценки задач'


class Meeting(models.Model):
    """
    Таблица назначенных встреч
    """
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                  related_name='organized_meetings',
                                  verbose_name='Организатор встречи')
    start_at = models.DateTimeField(verbose_name='Время начала встречи')
    end_at = models.DateTimeField(verbose_name='Время завершения встречи')
    participants = models.ManyToManyField(Profile,
                                          verbose_name='Участники встречи',
                                          related_name='participated_meetings')

    def __str__(self) -> str:
        return f'Встреча в {self.start_at}'

    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'


class Calendar(models.Model):
    """
    Таблица зарезервированных периодов времени для исполнителей и их руководителей
    """
    name = models.CharField(max_length=64, verbose_name='Название дела')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                              related_name='calendars',
                              verbose_name='Владелец зарезервированного времени')
    start_at = models.DateTimeField(verbose_name='Время начала дела')
    end_at = models.DateTimeField(verbose_name='Время окончания дела')

    def __str__(self) -> str:
        return f'Запланированное дело - {self.name}'

    class Meta:
        verbose_name = 'Зарезервированное время для дел'
        verbose_name_plural = 'Зарезервированное время для дел'
        constraints = (models.UniqueConstraint(fields=('name', 'owner', 'start_at', 'end_at'),
                                               name='Unique calendar constraint'),)
