import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from activities.models import News, Task, TaskStatus, TaskEstimation, Meeting, Calendar


class NewsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели News
    """
    id = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.user.username', read_only=True)

    class Meta:
        fields = ['id', 'title', 'content', 'author_name']
        model = News

        extra_kwargs = {
            'title': {'default': 'Заголовок новости'},
            'content': {'default': 'Содержание новости'}
        }


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task
    """
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(default=datetime.datetime.now())

    def validate(self, data):
        if data['created_at'].timestamp() >= data['deadline'].timestamp():
            raise ValidationError('Task beginning must be earlier than end of it...')
        return data

    class Meta:
        fields = ['id', 'name', 'assigned_by', 'assigned_to', 'created_at', 'deadline']
        model = Task

        extra_kwargs = {
            'assigned_by': {'read_only': True},
        }


class TaskStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TaskStatus
    """
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'task', 'status', 'comment']
        model = TaskStatus

        extra_kwargs = {
            'task': {'read_only': True},
        }


class TaskEstimationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TaskEstimation
    """
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'created_at', 'deadline_meeting', 'completeness', 'quality']
        model = TaskEstimation


class MeetingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Meeting
    """
    id = serializers.IntegerField(read_only=True)
    organizer_name = serializers.CharField(source='organizer.user.username',
                                           read_only=True, default='Имя организатора')

    def validate(self, data):
        if data['start_at'].timestamp() >= data['end_at'].timestamp():
            raise ValidationError('Task beginning must be earlier than end of it...')
        return data

    class Meta:
        fields = ['id', 'organizer_name', 'start_at', 'end_at', 'participants']
        model = Meeting

        extra_kwargs = {
            'participants': {'read_only': True}
        }


class CalendarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Calendar
    """
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'start_at', 'end_at', ]
        model = Calendar

        extra_kwargs = {
            'name': {'default': 'Название календаря'}
        }


class SuccessResponseWithStatus(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')
    data = TaskStatusSerializer()


class SuccessResponseWithMark(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')
    data = TaskEstimationSerializer()


class SuccessResponseWithNews(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')
    data = NewsSerializer()


class SuccessResponseWithMeeting(serializers.Serializer):
    message = serializers.CharField(default='Операция прошла удачно')
    data = MeetingSerializer()
