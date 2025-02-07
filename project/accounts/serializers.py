from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.constants import Position
from accounts.models import Profile
from activities.serializers import TaskEstimationSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User
    """
    id = serializers.IntegerField(read_only=True)
    is_staff = serializers.BooleanField(default=False)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        fields = ['id', 'username', 'password', 'is_staff', ]
        model = User

        extra_kwargs = {
            'username': {'default': 'Some name'},
        }


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile
    """
    detailed_position = serializers.ChoiceField(source='get_position_display',
                                                choices=Position.labels,
                                                read_only=True)
    name = serializers.CharField(source='user.username', read_only=True, default='Some name')
    company_name = serializers.CharField(source='team.name', read_only=True)
    team = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        fields = ['id', 'team', 'name', 'position', 'detailed_position',
                  'is_administrator', 'company_name']
        model = Profile
        extra_kwargs = {
            'team': {'write_only': True},
            'id': {'read_only': True},
            'position': {'write_only': True},
        }


class SuccessTokenResponse(serializers.Serializer):
    message = serializers.CharField(default='Token для текущего пользователя')
    token = serializers.CharField(default='Some secret token here...')


class SuccessResponse(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')


class SuccessResponseWithUser(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')
    data = UserSerializer()


class Error400Response(serializers.Serializer):
    message = serializers.CharField(default='Введенные данные некорректны')


class Error403Response(serializers.Serializer):
    message = serializers.CharField(default='Такой пользователь уже существует')


class Error404Response(serializers.Serializer):
    message = serializers.CharField(default='Объект не найден')
