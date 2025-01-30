from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Profile


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_staff = serializers.BooleanField(default=False, read_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        fields = ['id', 'username', 'password', 'is_staff']
        model = User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'user', 'team', 'position', 'is_administrator']
        model = Profile
