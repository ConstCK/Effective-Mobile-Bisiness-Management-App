import datetime
from http import HTTPMethod

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import Error400Response, Error404Response, SuccessResponse
from activities.models import News, Meeting, Calendar, Task, TaskStatus, TaskEstimation
from activities.serializers import NewsSerializer, MeetingSerializer, CalendarSerializer, TaskSerializer, \
    TaskStatusSerializer, TaskEstimationSerializer, SuccessResponseWithStatus, SuccessResponseWithMark, \
    SuccessResponseWithNews, SuccessResponseWithMeeting
from activities.utils import Service, BusyException, AlienException


@extend_schema(tags=['News'])
class NewsViewSet(viewsets.ModelViewSet, ):
    """
    Класс для операций с новостями.
    Доступно только администраторам.
    """
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsAdminUser, ]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'get', 'post', ]

    # Метод для получения компании.
    @extend_schema(summary='Получение новости',
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID новости',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Метод для получения списка компаний.
    @extend_schema(summary='Получение списка новостей', )
    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Создание новости
    @extend_schema(summary='Создание новости',
                   request=NewsSerializer,
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=SuccessResponseWithNews,
                           description='Успешное создание новости'
                       ),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка создания новости'),
                   },
                   )
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            news = News(**serializer.validated_data)
            news.author = Profile.objects.filter(user=request.user,
                                                 user__is_active=True).first()
            news.save()
            result = self.serializer_class(news, many=False)

            return Response({'message': 'Успешное создания новости.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка создания новостей.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


@extend_schema(tags=['Meeting'])
class MeetingViewSet(viewsets.ModelViewSet, Service):
    """
    Класс для операций со встречами.
    Доступно только администраторам.
    """
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    permission_classes = [IsAdminUser, ]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'get', 'post', 'delete']

    # Метод для получения данных о встрече.
    @extend_schema(summary='Получение данных о встрече',
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID компании',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Метод для получения списка встреч.
    @extend_schema(summary='Получение списка встреч',)
    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Создание встречи
    @extend_schema(summary='Создание встречи',
                   request=MeetingSerializer,
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=SuccessResponseWithMeeting,
                           description='Успешное создание встречи'
                       ),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка создания встречи'),
                   },
                   )
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Проверка на занятость руководителя в указанные даты встречи
            if not self.is_free(request.user, serializer.validated_data['start_at'],
                                serializer.validated_data['end_at']):
                raise BusyException('Time spot is busy issue')

            meeting = Meeting(**serializer.validated_data)
            meeting.organizer = (Profile.objects.filter(user=request.user, user__is_active=True)
                                 .first())
            meeting.save()

            # Добавление записи о занятом периоде времени в календарь
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
    @extend_schema(summary='Отмена встречи',
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешная отмена встречи'
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Ошибка отмены встречи'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка отмены встречи'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID встречи',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        try:
            # Очистка занятой встречей записи в календаре
            self.clear_calendar(kwargs.get('pk'))
            super().destroy(request, *args, **kwargs)

            return Response({'message': 'Успешная отмена встречи.'},
                            status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': 'Ошибка удаление встречи.'
                                        f'Неверный ID встречи.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка удаление встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Добавление участников встречи
    @extend_schema(summary='Добавление участников встречи',
                   responses={
                       status.HTTP_200_OK: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешное добавление участников встречи',
                           examples=[OpenApiExample(
                               name='Participants adding response',
                               description='Пример ответа после добавления участника встречи',
                               value={
                                   'message': 'Успешное добавление участника к встрече'
                               },
                           )
                           ],
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Ошибка добавление участников встречи'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка добавление участников встречи'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID встречи',
                           required=True,
                           type=int
                       ),
                   ],
                   examples=[
                       OpenApiExample(
                           name='Participants adding',
                           description='Пример вводимого имени участника встречи',
                           value={
                               'name': 'Имя участника',
                           },
                       )
                   ]
                   )
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='add-participant',
            permission_classes=[IsAdminUser, ])
    def add_participant(self, request: Request, *args, **kwargs) -> Response:
        try:
            user = User.objects.get(username=request.data['name'])
            participant = Profile.objects.filter(user=user, user__is_active=True).first()
            meeting = Meeting.objects.get(id=kwargs.get('pk'))

            # Проверка на принадлежность к одной команде руководителя и исполнителя
            if not self.is_same_team(request.user, user):
                raise AlienException('Not the same company members issue')

            # Проверка на занятость исполнителя в указанные даты встречи
            if not self.is_free(user, meeting.start_at, meeting.end_at):
                raise BusyException('Time spot is busy issue')

            meeting.participants.add(participant)
            meeting.save()

            # Добавление записи о занятом периоде времени в календарь
            Calendar.objects.create(name=f'Встреча {meeting.id}',
                                    owner=participant,
                                    start_at=meeting.start_at,
                                    end_at=meeting.end_at)

            return Response({'message': f'Успешное добавление участника {participant}'
                                        f' к встрече № {kwargs.get('pk')}.'
                             }, status=status.HTTP_200_OK, )

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
    @extend_schema(summary='Удаление участников встречи',
                   responses={
                       status.HTTP_200_OK: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешное удаление участников встречи',
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Ошибка удаления участников встречи'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка удаления участников встречи'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID встречи',
                           required=True,
                           type=int
                       ),
                   ],
                   examples=[
                       OpenApiExample(
                           name='Participants deletion',
                           description='Пример вводимого имени участника встречи',
                           value={
                               'name': 'Имя участника',
                           },
                       )
                   ]
                   )
    @action(methods=[HTTPMethod.DELETE, ], detail=True, url_path='delete-participant',
            permission_classes=[IsAdminUser, ])
    def delete_participant(self, request: Request, *args, **kwargs) -> Response:
        try:
            user = User.objects.get(username=request.data['name'])
            participant = Profile.objects.filter(user=user, user__is_active=True).first()
            meeting = Meeting.objects.get(id=kwargs.get('pk'))

            meeting.participants.remove(participant)
            meeting.save()

            # Удаление записи о занятом периоде времени из календаря
            calendar = Calendar.objects.get(name=f'Встреча {meeting.id}',
                                            owner=participant,
                                            start_at=meeting.start_at,
                                            end_at=meeting.end_at)

            calendar.delete()

            return Response({'message': f'Успешное удаление участника {participant}'
                                        f' из встречи № {kwargs.get('pk')}.'
                             }, status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': 'Ошибка удаления участника встречи.'
                                        f'Неверный ID встречи или имя участника.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка добавления участника встречи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


@extend_schema(tags=['Calendar'])
class CalendarViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с календарем.
    """

    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()
    permission_classes = [IsAuthenticated, ]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'get']

    # Просмотр календаря текущего пользователя за текущий день/ месяц
    @extend_schema(summary='Просмотр календаря текущего пользователя',
                   responses={
                       status.HTTP_200_OK: OpenApiResponse(
                           response=CalendarSerializer,
                           description='Успешное получение календаря'
                       ),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка получения данных'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='period',
                           location=OpenApiParameter.QUERY,
                           description='Параметр для определения периода календаря'
                                       ' (daily - для ежедневного/monthly - для ежемесячного)',
                           required=True,
                           type=str
                       ),
                   ],
                   )
    def list(self, request: Request, *args, **kwargs) -> Response:
        profile = Profile.objects.filter(user=request.user, user__is_active=True).first()
        today = datetime.date.today()

        # Выбор отображения записей календаря в зависимости от указанного в query params периода
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

    # Отключение метода для ViewSet.
    @extend_schema(summary='Метод недоступен!')
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(tags=['Task'])
class TaskViewSet(viewsets.ModelViewSet, Service):
    """
    Класс для операций с задачами сотрудникам.
    """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAdminUser, ]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'post', 'put', 'delete']

    # Создание задачи администратором для сотрудников с присвоением статуса "Выполняется".
    # Заполнение календаря для сотрудника.
    @extend_schema(summary='Создание задачи администратором для сотрудников',
                   request=TaskSerializer,
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=TaskSerializer,
                           description='Успешное создание задачи'
                       ),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка создания задачи'),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Объект не найден'),
                   },
                   examples=[
                       OpenApiExample(
                           'Task creation example',
                           description='Пример вводимых данных задачи',
                           value={
                               'name': 'Название задачи',
                               'assigned_to': 'ID исполнителя',
                               'deadline': '2025-02-14T17:00:00'
                           },
                       )
                   ]
                   )
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            executor = User.objects.get(profile__id=request.data['assigned_to'])
            created_at = timezone.now()
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Проверка на принадлежность к одной команде руководителя и исполнителя
            if not self.is_same_team(request.user, executor):
                raise AlienException('Not the same company members issue')

            task = Task(**serializer.validated_data)
            task.assigned_by = Profile.objects.filter(user=request.user,
                                                      user__is_active=True).first()
            task.save()
            result = TaskSerializer(task)

            # Добавление записи в календарь о времени выполнения задачи
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
            return Response({'message': 'Ошибка назначения задачи.'
                                        f'Неверный ID исполнителя.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка создания задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Обновление задачи администратором.
    @extend_schema(summary='Обновление задачи администратором',
                   request=TaskSerializer,
                   responses={
                       status.HTTP_202_ACCEPTED: OpenApiResponse(
                           response=TaskSerializer,
                           description='Успешное обновление задачи'
                       ),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка обновления задачи'),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Объект не найден'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для определения ID задачи',
                           required=True,
                           type=int
                       ),
                   ],
                   examples=[
                       OpenApiExample(
                           'Task update example',
                           description='Пример вводимых данных задачи',
                           value={
                               'name': 'Название задачи',
                               'assigned_to': 'ID исполнителя',
                               'deadline': '2025-02-14T17:00:00'
                           },
                       )
                   ]
                   )
    def update(self, request: Request, *args, **kwargs) -> Response:
        try:
            task = Task.objects.get(id=kwargs.get('pk'))
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Проверка на принадлежность к одной команде руководителя и исполнителя
            if not self.is_same_team(request.user,
                                     User.objects.get(profile__id=request.data['assigned_to'])):
                raise AlienException('Not the same company members issue')

            # Удаление записи из календаря о времени выполнения задачи для предыдущего исполнителя
            calendar = Calendar.objects.get(name=f'Задача {kwargs.get('pk')}')
            calendar.delete()

            task.assigned_to = serializer.validated_data['assigned_to']
            task.name = serializer.validated_data['name']
            task.deadline = serializer.validated_data['deadline']
            task.save()

            result = TaskSerializer(task)

            # Добавление записи в календарь о новой задаче
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
            return Response({'message': 'Ошибка обновления задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка обновления задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление задачи администратором.
    @extend_schema(summary='Удаление задачи администратором',
                   responses={
                       status.HTTP_202_ACCEPTED: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешное удаление задачи'
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Объект не найден'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для определения ID задачи',
                           required=True,
                           type=int
                       ),
                   ],
                   )
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
            return Response({'message': 'Ошибка удаления задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )

    # Изменение статуса задачи исполнителем с добавлением комментария.
    @extend_schema(summary='Изменение статуса задачи исполнителем',
                   request=TaskStatusSerializer,
                   responses={
                       status.HTTP_202_ACCEPTED: OpenApiResponse(
                           response=SuccessResponseWithStatus,
                           description='Успешное изменение статуса'
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Объект не найден'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка добавления данных'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для определения ID задачи',
                           required=True,
                           type=int
                       ),
                   ],
                   examples=[
                       OpenApiExample(
                           'Task status update example',
                           description='Пример вводимых данных статуса задачи',
                           value={
                               "status": "FINISHED/DEFERRED",
                               "comment": "Комментарий к задаче"
                           },
                       )
                   ]
                   )
    @action([HTTPMethod.POST, ], detail=True, url_path='update-status',
            permission_classes=[IsAuthenticated, ])
    def update_status(self, request: Request, *args, **kwargs) -> Response:
        try:
            # Поверка на принадлежность задачи исполнителю
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
            return Response({'message': 'Ошибка обновления статуса задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка обновления статуса задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Оценка задачи начальником.
    @extend_schema(summary='Оценка задачи начальником',
                   request=TaskEstimationSerializer,
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=SuccessResponseWithMark,
                           description='Успешное выставление оценки задаче'
                       ),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Объект не найден'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка добавления данных'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для определения ID задачи',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    @action([HTTPMethod.POST, ], detail=True, url_path='estimate-task', )
    def estimate_task(self, request: Request, *args, **kwargs) -> Response:
        try:
            # Поверка на принадлежность задачи профилю, присвоившую ее
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
            return Response({'message': 'Ошибка оценки задачи.'
                                        f'Неверный ID задачи.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Ошибка оценки задачи.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )
