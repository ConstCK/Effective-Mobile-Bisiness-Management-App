import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Profile
from activities.models import Meeting, Calendar


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
        try:
            person = Profile.objects.get(user=user)
            person_calendars = person.calendars
            if person_calendars.exists():
                for i in person_calendars.values():
                    if i['name'].startswith('Встреча') and (i['end_at'] >= start_time >= i['start_at']
                                                            or i['end_at'] >= end_time >= i['start_at']):
                        return False

        except ObjectDoesNotExist:
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
        organizer = Profile.objects.get(user=organizer)
        staff = Profile.objects.get(user=staff)
        return organizer.team == staff.team
