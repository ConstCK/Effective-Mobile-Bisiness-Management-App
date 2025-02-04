import datetime
from http import HTTPMethod

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from activities.models import News, Meeting, Calendar, Task, TaskStatus, TaskEstimation
from activities.serializers import NewsSerializer, MeetingSerializer, CalendarSerializer, TaskSerializer, \
    TaskStatusSerializer, TaskEstimationSerializer
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
            news.author = Profile.objects.filter(user=request.user, user__is_active=True).first()
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
            meeting.organizer = (Profile.objects.filter(user=request.user, user__is_active=True)
                                 .first())
            meeting.save()
            Calendar.objects.create(name=f'Встреча {meeting.id}',
                                    owner=Profile.objects.get(user=request.user),
                                    start_at=meeting.start_at,
                                    end_at=meeting.end_at)
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
            participant = Profile.objects.filter(user=user, user__is_acrive=True).first()
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
            participant = Profile.objects.filter(user=user, user__is_acrive=True).first()
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
                             }, status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка удаления участника встречи.'
                                        f'Неверный ID встречи или имя участника.'},
                            status=status.HTTP_404_NOT_FOUND, )

        except Exception as error:
            return Response({'message': f'Ошибка добавления участника встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

        # Изменение времени встречи (???)
        @action(methods=[HTTPMethod.DELETE, ], detail=True, url_path='update-meeting',
                permission_classes=[IsAdminUser, ])
        def update_meeting(self, request: Request, *args, **kwargs) -> Response:
            pass


class CalendarViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с календарем.
    """

    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()
    permission_classes = [IsAuthenticated, ]

    # Просмотр календаря текущего пользователя за текущий день/ месяц
    def list(self, request: Request, *args, **kwargs) -> Response:
        profile = Profile.objects.filter(user=request.user, user__is_active=True).first()
        today = datetime.date.today()

        if request.query_params['period'] == 'daily':
            calendar = Calendar.objects.filter(owner=profile, start_at__date=today)
        elif request.query_params['period'] == 'monthly':
            calendar = Calendar.objects.filter(owner=profile, start_at__month=today.month)
        else:
            return Response({'message': f'Ошибка получения календаря.'
                                        f'Возможно неверно указан режим (daily/monthly).'},
                            status=status.HTTP_400_BAD_REQUEST, )

        serializer = self.serializer_class(calendar, many=True)

        return Response({'message': serializer.data},
                        status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet, Service):
    """
    Класс для операций с задачами сотрудникам.
    """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAdminUser, ]

    # Создание задачи администратором для сотрудников с присвоением статуса "Выполняется".
    # Заполнение календаря для сотрудника.
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            executor = User.objects.get(profile__id=request.data['assigned_to'])
            created_at = timezone.now()
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            if not self.is_same_team(request.user, executor):
                raise AlienException('Not the same company members issue')

            task = Task(**serializer.validated_data)
            task.assigned_by = Profile.objects.filter(user=request.user,
                                                      user__is_active=True).first()
            task.save()
            result = TaskSerializer(task)

            Calendar.objects.create(name=f'Задача {result.data['id']}',
                                    owner=Profile.objects.get(user=executor),
                                    start_at=created_at,
                                    end_at=serializer.validated_data['deadline'])
            TaskStatus.objects.create(task=task, status='PENDING')

            return Response({'message': 'Успешное создания задачи.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )

        except AlienException:
            return Response({'message': 'Ошибка назначения задачи.'
                                        'Исполнитель задачи - сотрудник другой компании.'},
                            status=status.HTTP_400_BAD_REQUEST, )
        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка назначения задачи.'
                                        f'Неверный ID исполнителя.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка создания задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Создание задачи администратором для сотрудников.
    def update(self, request: Request, *args, **kwargs) -> Response:
        try:
            task = Task.objects.get(id=kwargs.get('pk'))
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.data['assigned_to']:
                if not self.is_same_team(request.user,
                                         User.objects.get(profile__id=request.data['assigned_to'])):
                    raise AlienException('Not the same company members issue')
                calendar = Calendar.objects.get(name=f'Задача {kwargs.get('pk')}')
                calendar.delete()
                task.assigned_to = serializer.validated_data['assigned_to']
            if serializer.data['name']:
                task.name = serializer.validated_data['name']
            if serializer.data['deadline']:
                task.deadline = serializer.validated_data['deadline']

            task.save()
            result = TaskSerializer(task)
            Calendar.objects.create(name=f'Задача {kwargs.get('pk')}',
                                    owner=task.assigned_to,
                                    start_at=task.created_at,
                                    end_at=task.deadline, )
            return Response({'message': 'Успешное обновление задачи.',
                             'data': result.data},
                            status=status.HTTP_202_ACCEPTED, )

        except AlienException:
            return Response({'message': 'Ошибка обновления задачи.'
                                        'Исполнитель задачи - сотрудник другой компании.'},
                            status=status.HTTP_400_BAD_REQUEST, )
        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка обновления задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка обновления задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление задачи администратором.
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        try:
            task = Task.objects.get(id=kwargs.get('pk'))
            calendar = Calendar.objects.get(name=f'Задача {kwargs.get('pk')}',
                                            owner=task.assigned_to)
            task.delete()
            calendar.delete()

            return Response({'message': 'Успешное удаление задачи.'},
                            status=status.HTTP_200_OK, )
        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка удаления задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )

    # Изменение статуса задачи исполнителем с добавлением комментария.
    @action([HTTPMethod.POST, ], detail=True, url_path='update-status',
            permission_classes=[IsAuthenticated, ])
    def update_status(self, request: Request, *args, **kwargs) -> Response:
        try:
            if not self.is_task_executor(kwargs.get('pk'),
                                         User.objects.get(username=request.user)):
                raise AlienException('Not correct executor issue')
            serializer = TaskStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task_status = TaskStatus.objects.get(task=Task.objects.get(pk=kwargs.get('pk')))
            task_status.status = serializer.validated_data['status']
            task_status.comment = serializer.validated_data['comment']
            task_status.save()

            result = TaskStatusSerializer(task_status)
            return Response({'message': 'Успешное обновление статуса задачи.',
                             'data': result.data},
                            status=status.HTTP_202_ACCEPTED, )

        except AlienException:
            return Response({'message': 'Ошибка обновления статуса задачи.'
                                        'Обновления статуса доступно только для сотрудника задачи.'},
                            status=status.HTTP_400_BAD_REQUEST, )

        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка обновления статуса задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )

        except Exception as error:
            return Response({'message': f'Ошибка обновления статуса задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Оценка задачи начальником.
    @action([HTTPMethod.POST, ], detail=True, url_path='estimate-task',)
    def estimate_task(self, request: Request, *args, **kwargs) -> Response:
        try:
            if not self.is_task_assignor(kwargs.get('pk'),
                                         User.objects.get(username=request.user)):
                raise AlienException('Not correct assignor issue')
            serializer = TaskEstimationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task_estimation = TaskEstimation(**serializer.data)
            task_estimation.task = Task.objects.get(id=kwargs.get('pk'))
            task_estimation.save()

            result = TaskEstimationSerializer(task_estimation)
            return Response({'message': 'Успешная оценка задачи.',
                             'data': result.data},
                            status=status.HTTP_202_ACCEPTED, )

        except AlienException:
            return Response({'message': 'Ошибка оценки задачи.'
                                        'Оценка доступна только для начальника,'
                                        ' назначившего задачу задачи.'},
                            status=status.HTTP_400_BAD_REQUEST, )

        except ObjectDoesNotExist:
            return Response({'message': f'Ошибка оценки задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )

        except Exception as error:
            return Response({'message': f'Ошибка оценки задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


