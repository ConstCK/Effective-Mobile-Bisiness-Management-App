from http import HTTPMethod

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс для регистрации пользователя, изменения данных и удаления профиля.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # Регистрация нового пользователя
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = User.objects.create_user(username=serializer.validated_data['username'],
                                                password=serializer.validated_data['password'],
                                                is_staff=serializer.validated_data['is_staff'])
                token = Token.objects.create(user=user)
                return Response({'message': 'Успешная регистрация пользователя',
                                 'user': {'id': user.id, 'username': user.username},
                                 'token': token.key},
                                status=status.HTTP_201_CREATED, )
        except IntegrityError as error:
            return Response({'message': f'Невозможно зарегистрировать пользователя.'
                                        f'Такой пользователь уже существует.'
                                        f'Детали ошибки: {error}...'},
                            status=status.HTTP_403_FORBIDDEN, )
        except Exception as error:
            return Response({'message': f'Ошибка регистрации.'
                                        f'Детали ошибки {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Получение токена по имени и паролю
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

    # Обновление данных пользователя
    @action(methods=[HTTPMethod.PATCH, ], detail=False, url_path='update-profile')
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
                            status=status.HTTP_200_OK, )
        except Exception as error:
            return Response({'message': f'Ошибка обновления данных профиля.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление данных пользователя
    @action(methods=[HTTPMethod.DELETE, ], detail=False, url_path='delete-profile')
    def delete_profile(self, request: Request, *args, **kwargs) -> Response:

        user = request.user
        instance = User.objects.filter(username=user)
        if instance.objects.exist():
            instance.is_active = False

            return Response({'message': f'Данные профиля успешно удалены.'},
                            status=status.HTTP_200_OK, )

    # Изменение статуса пользователя (апгрейд до администратора)
    @action(methods=[HTTPMethod.GET, ], detail=True, url_path='upgrade-profile')
    def upgrade_profile(self, request: Request, *args, **kwargs) -> Response:

        user = request.user
        print(user)
        if user.is_staff:

            try:
                instance = Profile.objects.get(pk=kwargs.get('pk'))
                print(instance)
                instance.is_administrator = True
                instance.user.is_staff = True
                instance.save()
                instance.user.save()
                return Response({'message': f'{instance.user} - теперь администратор.'},
                                status=status.HTTP_200_OK, )

            except Exception:
                return Response({'message': f'Профиль с указанным ID не существует.'},
                                status=status.HTTP_404_NOT_FOUND, )
        else:
            return Response({'message': f'У Вас нет прав изменять статус сотрудников.'},
                            status=status.HTTP_400_BAD_REQUEST, )
