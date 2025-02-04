import datetime
from http import HTTPMethod

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Avg
from django.db.models.functions import Round
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import UserSerializer, ProfileSerializer
from activities.models import Task, TaskEstimation
from activities.serializers import TaskSerializer, TaskEstimationSerializer
from activities.utils import Service
from companies.models import Company


class UserViewSet(viewsets.ModelViewSet, Service):
    """
    Класс для регистрации пользователя, изменения данных и удаления профиля.
    Авторизация пользователя происходит путем передачи токена в заголовке запроса.
    Пример заголовка-> Authorization: Token fe663987c55934a4888044d3e560c6194534b25c
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny, ]

    # Регистрация нового пользователя.
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create_user(username=serializer.validated_data['username'],
                                            password=serializer.validated_data['password'],
                                            is_staff=serializer.validated_data['is_staff'])
            token = Token.objects.create(user=user)
            if 'team' in request.data:
                company = Company.objects.filter(pk=request.data['team']).first()
                profile = Profile.objects.create(user=user, is_administrator=user.is_staff,
                                                 team=company)

            else:
                profile = Profile.objects.create(user=user, is_administrator=user.is_staff, )

            if user.is_staff:
                profile.position = 'MANAGER'
                profile.save()

            result = ProfileSerializer(profile)

            return Response({'message': 'Успешная регистрация пользователя',
                             'profile': result.data,
                             'token': token.key,
                             },
                            status=status.HTTP_201_CREATED, )
        except IntegrityError as error:
            return Response({'message': f'Невозможно зарегистрировать пользователя.'
                                        f'Такой пользователь уже существует.'
                                        f'Детали ошибки: {error}...'},
                            status=status.HTTP_403_FORBIDDEN, )
        except Exception as error:
            return Response({'message': f'Ошибка регистрации.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Получение токена по имени и паролю.
    @action(methods=[HTTPMethod.POST, ], detail=False, url_path='get-token')
    def get_token(self, request: Request) -> Response:

        user = authenticate(request,
                            username=request.data['username'],
                            password=request.data['password'])

        if user:
            token = Token.objects.filter(user_id=user.id).first()
            return Response({'message': f'Token для пользователя {user.username}',
                             'token': token.key},
                            status=status.HTTP_200_OK, )
        return Response({'message': f'Пользователь {request.data['username']} не зарегистрирован'},
                        status=status.HTTP_400_BAD_REQUEST, )

    # Обновление данных пользователя. Можно изменить только пароль.
    @action(methods=[HTTPMethod.PATCH, ], detail=False, url_path='update-profile',
            permission_classes=[IsAuthenticated])
    def update_profile(self, request: Request, *args, **kwargs) -> Response:

        try:
            user = request.user
            serializer = self.serializer_class(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            user.username = request.user.username
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': f'Данные профиля успешно обновлены.',
                             'user': {'id': user.id, 'username': user.username,
                                      'is_staff': user.is_staff},
                             },
                            status=status.HTTP_202_ACCEPTED, )
        except Exception as error:
            return Response({'message': f'Ошибка обновления данных профиля.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление данных пользователя (своего профиля).
    @action(methods=[HTTPMethod.DELETE, ], detail=False, url_path='delete-profile',
            permission_classes=[IsAuthenticated])
    def delete_profile(self, request: Request, *args, **kwargs) -> Response:
        try:
            instance = User.objects.get(username=request.user)
            if instance:
                instance.is_active = False
                instance.save()

                return Response({'message': f'Данные профиля успешно удалены.'},
                                status=status.HTTP_200_OK, )
        except Exception as error:
            return Response({'message': f'Профиль с указанным ID не существует.{error}'},
                            status=status.HTTP_404_NOT_FOUND, )

    # Изменение статуса пользователя (апгрейд до администратора)
    @action(methods=[HTTPMethod.GET, ], detail=True, url_path='upgrade-profile',
            permission_classes=[IsAdminUser, ])
    def upgrade_profile(self, request: Request, *args, **kwargs) -> Response:
        try:
            instance = Profile.objects.filter(pk=kwargs.get('pk'), user__is_active=True).first()
            instance.is_administrator = True
            instance.user.is_staff = True
            instance.save()
            instance.user.save()
            return Response({'message': f'{instance.user} - теперь администратор.'},
                            status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': f'Профиль с указанным ID не существует.'},
                            status=status.HTTP_404_NOT_FOUND, )

    # Изменение должности пользователя (доступно только генеральному менеджеру)
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='change-position-profile',
            permission_classes=[IsAdminUser, ])
    def change_profile_position(self, request: Request, *args, **kwargs) -> Response:
        if request.user.profile.position != 'BOSS':
            return Response({'message': 'Смена должностей сотрудников доступна только для генерального менеджера'},
                            status=status.HTTP_403_FORBIDDEN, )
        if request.data['position'] == 'BOSS':
            return Response({'message': 'Ошибка...Может быть только один генеральный менеджер.'},
                            status=status.HTTP_400_BAD_REQUEST, )
        try:
            instance = Profile.objects.filter(pk=kwargs.get('pk'), user__is_active=True).first()
            serializer = ProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.position = serializer.validated_data['position']
            instance.save()
            result = ProfileSerializer(instance)

            return Response({'message': f'{result.data['name']} - теперь {result.data['detailed_position']}.'},
                            status=status.HTTP_202_ACCEPTED, )

        except ObjectDoesNotExist:
            return Response({'message': f'Профиль с указанным ID не существует.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Не удалось обновить профиль.'
                                        f'Детали ошибки: {error}'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Изменение компании пользователя (доступно только менеджеру)
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='add-profile-to-company',
            permission_classes=[IsAdminUser, ])
    def change_profile_team(self, request: Request, *args, **kwargs) -> Response:

        try:
            instance = Profile.objects.filter(pk=kwargs.get('pk'), user__is_active=True).first()
            company = Company.objects.get(pk=request.data['team'])
            instance.team = company
            instance.save()

            return Response({'message': f'{instance.user} - теперь в {company.name}.'},
                            status=status.HTTP_202_ACCEPTED, )

        except ObjectDoesNotExist:
            return Response({'message': f'Профиль или компания с указанным ID не существует.'},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as error:
            return Response({'message': f'Не удалось обновить профиль.'
                                        f'Детали ошибки: {error}'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Получение списка профилей для администратора
    def list(self, request: Request, *args, **kwargs) -> Response:
        if request.user.is_staff:
            query = Profile.objects.filter(user__is_active=True)
            serializer = ProfileSerializer(query, many=True)
            return Response({'message': serializer.data},
                            status=status.HTTP_200_OK)
        return Response({'message': 'У Вас недостаточно прав для получения этой информации'},
                        status=status.HTTP_403_FORBIDDEN)

    # Получение всех своих оценок.
    @action([HTTPMethod.GET, ], detail=False, url_path='get-marks',
            permission_classes=[IsAuthenticated])
    def get_marks(self, request: Request, *args, **kwargs) -> Response:
        try:
            quarter = self.determine_quarter()
            tasks = Task.objects.filter(assigned_to=Profile.objects.get(user=request.user))

            if request.query_params.get('options') == 'quarter':
                tasks = tasks.filter(taskestimation__created_at__month__gte=quarter[0],
                                     taskestimation__created_at__month__lte=quarter[1], )
                result = tasks.aggregate(
                    average_deadline_meeting=Round(Avg('taskestimation__deadline_meeting', default=0), 2),
                    average_completeness=Round(Avg('taskestimation__completeness', default=0), 2),
                    average_quality=Round(Avg('taskestimation__quality', default=0), 2)
                )

                return Response({'message': 'Средние оценки исполнителя за текущий квартал',
                                 'data': {'Соответствие дедлайн': result['average_deadline_meeting'],
                                          'Завершение задачи': result['average_completeness'],
                                          'Качество выполнения': result['average_quality']}},
                                status=status.HTTP_200_OK)

            if request.query_params.get('options') == 'company':
                current_team = Profile.objects.get(user=request.user).team
                profiles = Profile.objects.filter(team=current_team)
                tasks = tasks.filter(assigned_to__in=profiles)
                result = tasks.aggregate(
                    average_deadline_meeting=Round(Avg('taskestimation__deadline_meeting', default=0), 2),
                    average_completeness=Round(Avg('taskestimation__completeness', default=0), 2),
                    average_quality=Round(Avg('taskestimation__quality', default=0), 2)
                )

                return Response({'message': 'Средние оценки исполнителя в компании',
                                 'data': {'Соответствие дедлайн': result['average_deadline_meeting'],
                                          'Завершение задачи': result['average_completeness'],
                                          'Качество выполнения': result['average_quality']}},
                                status=status.HTTP_200_OK)
            else:
                all_marks = TaskEstimation.objects.filter(task__in=tasks)
                result = TaskEstimationSerializer(all_marks, many=True)
                return Response({'message': 'Все оценки пользователя за задачи',
                                 'data': result.data},
                                status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'message': f'Не удалось отобразить список оценок.'
                                        f'Детали ошибки: {error}'},
                            status=status.HTTP_400_BAD_REQUEST, )
