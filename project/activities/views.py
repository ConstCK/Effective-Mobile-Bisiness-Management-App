import datetime
from http import HTTPMethod

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from activities.models import News, Meeting, Calendar
from activities.serializers import NewsSerializer, MeetingSerializer, CalendarSerializer
from activities.utils import Service, BusyException, AlienException


class NewsViewSet(viewsets.ModelViewSet, ):
    """
    Класс для операций с новостями.
    Доступно только администраторам.
    """
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsAdminUser, ]

    # Создание новости
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            news = News(**serializer.validated_data)
            news.author = Profile.objects.get(user=request.user)
            news.save()
            result = self.serializer_class(news, many=False)
            return Response({'message': 'Успешное создания новости.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка создания новостей.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


class MeetingViewSet(viewsets.ModelViewSet, Service):
    """
    Класс для операций со встречами.
    Доступно только администраторам.
    """
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    permission_classes = [IsAdminUser, ]

    # Создание встречи
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            if not self.is_free(request.user, serializer.validated_data['start_at'],
                                serializer.validated_data['end_at']):
                raise BusyException('Time spot is busy issue')
            meeting = Meeting(**serializer.validated_data)
            meeting.organizer = Profile.objects.get(user=request.user)
            meeting.save()
            Calendar.objects.create(name=f'Встреча {meeting.id}',
                                    owner=Profile.objects.get(user=request.user),
                                    start_at=meeting.start_at,
                                    end_at=meeting.end_at)
            # person.calendars.add(calendar)
            result = self.serializer_class(meeting, many=False)

            return Response({'message': 'Успешное создания встречи.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )
        except BusyException:
            return Response({'message': 'В это время Вы не сможете провести встречу.'},
                            status=status.HTTP_400_BAD_REQUEST, )

        except Exception as error:
            return Response({'message': f'Ошибка создания встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Отмена встречи
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        try:
            self.clear_calendar(kwargs.get('pk'))
            super().destroy(request, *args, **kwargs)

            return Response({'message': 'Успешное удаление встречи.'},
                            status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка удаление встречи.'
                                        f'Неверный ID встречи.'},
                            status=status.HTTP_404_NOT_FOUND, )

        except Exception as error:
            return Response({'message': f'Ошибка удаление встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Добавление участников встречи
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='add-participant',
            permission_classes=[IsAdminUser, ])
    def add_participant(self, request: Request, *args, **kwargs) -> Response:
        try:
            user = User.objects.get(username=request.data['name'])
            participant = Profile.objects.get(user=user)
            meeting = Meeting.objects.get(id=kwargs.get('pk'))

            if not self.is_same_team(request.user, user):
                raise AlienException('Not the same company members issue')

            if not self.is_free(user, meeting.start_at, meeting.end_at):
                raise BusyException('Time spot is busy issue')

            meeting.participants.add(participant)
            meeting.save()
            Calendar.objects.create(name=f'Встреча {meeting.id}',
                                    owner=participant,
                                    start_at=meeting.start_at,
                                    end_at=meeting.end_at)
            return Response({'message': f'Успешное добавление участника {participant}'
                                        f' к встрече № {kwargs.get('pk')}.'
                             }, status=status.HTTP_201_CREATED, )

        except AlienException:
            return Response({'message': 'Ошибка добавления участника встречи.'
                                        'Участник встречи - сотрудник другой компании.'},
                            status=status.HTTP_400_BAD_REQUEST, )
        except BusyException:
            return Response({'message': 'В это время участник будет занят.'},
                            status=status.HTTP_400_BAD_REQUEST, )
        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка добавления участника встречи.'
                                        f'Неверный ID встречи или имя участника.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка добавления участника встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление участников встречи
    @action(methods=[HTTPMethod.DELETE, ], detail=True, url_path='delete-participant',
            permission_classes=[IsAdminUser, ])
    def delete_participant(self, request: Request, *args, **kwargs) -> Response:
        try:
            user = User.objects.get(username=request.data['name'])
            participant = Profile.objects.get(user=user)
            meeting = Meeting.objects.get(id=kwargs.get('pk'))

            meeting.participants.remove(participant)
            meeting.save()
            calendar = Calendar.objects.get(name=f'Встреча {meeting.id}',
                                            owner=participant,
                                            start_at=meeting.start_at,
                                            end_at=meeting.end_at)

            calendar.delete()

            return Response({'message': f'Успешное удаление участника {participant}'
                                        f' из встречи № {kwargs.get('pk')}.'
                             }, status=status.HTTP_201_CREATED, )

        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка удаления участника встречи.'
                                        f'Неверный ID встречи или имя участника.'},
                            status=status.HTTP_404_NOT_FOUND, )

        except Exception as error:
            return Response({'message': f'Ошибка добавления участника встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


class CalendarViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с календарем.
    """

    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()

    # Просмотр календаря текущего пользователя за текущий день/ месяц
    def list(self, request: Request, *args, **kwargs) -> Response:
        profile = Profile.objects.get(user=request.user)
        today = datetime.date.today()


        if request.query_params['period'] == 'daily':
            calendar = Calendar.objects.filter(owner=profile, start_at__date=today)
        elif request.query_params['period'] == 'monthly':
            calendar = Calendar.objects.filter(owner=profile,  start_at__month=today.month)
        else:
            return Response({'message': f'Ошибка получения календаря.'
                                        f'Возможно неверно указан режим (daily/monthly).'},
                            status=status.HTTP_400_BAD_REQUEST, )

        serializer = self.serializer_class(calendar, many=True)

        return Response({'message': serializer.data},
                        status=status.HTTP_200_OK)
