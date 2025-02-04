import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Profile
from activities.models import Meeting, Calendar, Task


class BusyException(Exception):
    pass


class AlienException(Exception):
    pass


class Service:
    """
    Утилиты для проверки корректности запросов и ответов
    """

    # Метод для проверки календаря на свободное время
    @staticmethod
    def is_free(user: User, start_time: datetime, end_time: datetime) -> bool:
        person = Profile.objects.filter(user=user, user__is_active=True).first()
        person_calendars = person.calendars
        if person_calendars.exists():
            for i in person_calendars.values():
                if i['name'].startswith('Встреча') and (i['end_at'] >= start_time >= i['start_at']
                                                        or i['end_at'] >= end_time >= i['start_at']):
                    return False

        return True

    # Метод для очистки календаря при отмене собраний
    @staticmethod
    def clear_calendar(meeting_id: int) -> None:
        participants = Profile.objects.filter(participated_meetings=meeting_id)
        organizer = Meeting.objects.get(id=meeting_id).organizer
        staff = [i.id for i in participants]
        staff.append(organizer.id)
        calendars = Calendar.objects.filter(owner_id__in=staff, name=f'Встреча {meeting_id}')
        calendars.delete()

    # Метод для проверки сотрудника на принадлежность к компании организатора
    @staticmethod
    def is_same_team(organizer: User, staff: User) -> bool:
        organizer = Profile.objects.filter(user=organizer, user__is_active=True).first()
        staff = Profile.objects.filter(user=staff, user__is_active=True).first()
        return organizer.team == staff.team

    # Метод для проверки сотрудника на принадлежность к выполнению задачи
    @staticmethod
    def is_task_executor(task_id: int, user: User) -> bool:
        executor = Profile.objects.filter(user=user, user__is_active=True).first()
        task = Task.objects.get(id=task_id)
        return task.assigned_to == executor

    # Метод для проверки начальника на принадлежность к назначению задачи
    @staticmethod
    def is_task_assignor(task_id: int, user: User) -> bool:
        assignor = Profile.objects.filter(user=user, user__is_active=True).first()
        task = Task.objects.get(id=task_id)
        return task.assigned_by == assignor

    # Метод для определения текущего квартала
    @staticmethod
    def determine_quarter() -> tuple[int, int]:
        this_month = datetime.date.today().month
        if 1 <= this_month <= 3:
            quarter = (1, 3)
        elif 4 <= this_month <= 6:
            quarter = (4, 6)
        elif 7 <= this_month <= 9:
            quarter = (7, 9)
        else:
            quarter = (10, 12)
        return quarter
