from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.constants import Position
from accounts.models import Profile


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


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile
    """
    detailed_position = serializers.ChoiceField(source='get_position_display',
                                                choices=Position.labels,
                                                read_only=True)
    name = serializers.CharField(source='user.username', read_only=True)
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
