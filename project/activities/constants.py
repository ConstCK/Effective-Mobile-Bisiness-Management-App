from django.utils.translation import gettext_lazy as _
from django.db import models


class TaskStatuses(models.TextChoices):
    PENDING = 'PENDING', _('Выполняется')
    DEFERRED = 'DEFERRED', _('Отложено')
    FINISHED = 'FINISHED', _('Выполнено')


class TestActivityData:
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
    news_1 = {
        'title': 'News 1',
        'content': 'Some content here'
    }
    news_2 = {
        'title': 'News 2',
        'content': 'Another content here'
    }
    meeting_1 = {
        'start_at': '2025-02-10T18:00:00',
        'end_at': '2025-02-10T18:30:00'
    }
    meeting_2 = {
        'start_at': '2025-02-11T12:00:00',
        'end_at': '2025-02-11T18:00:00'
    }
    meeting_3 = {
        'start_at': '2025-02-10T18:00:00',
        'end_at': '2025-02-09T18:30:00'
    }
    task_1 = {
        'name': 'Task 1',
        'assigned_to': 2,
        'deadline': '2025-02-23T12:00:00'
    }
    task_2 = {
        'name': 'Task 2',
        'assigned_to': 2,
        'deadline': '2025-02-23T12:00:00'
    }
    new_task = {
        'name': 'New Task 1',
        'assigned_to': 2,
        'deadline': '2025-02-24T12:00:00'
    }
    new_status = {
        'status': 'FINISHED',
        'comment': 'Комментарий к задаче'
    }
    task_mark_1 = {
        'deadline_meeting': '3',
        'completeness': '7',
        'quality': '2'
    }
