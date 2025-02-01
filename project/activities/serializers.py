from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.serializers import ProfileSerializer
from activities.models import News, Task, TaskStatus, TaskEstimation, Meeting, Calendar


class NewsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.user.username', read_only=True)

    class Meta:
        fields = ['id', 'title', 'content', 'author_name']
        model = News


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        if data['created_at'] >= data['deadline']:
            raise ValidationError('Task beginning must be earlier than end of it...')
        return data

    class Meta:
        fields = ['id', 'name', 'assigned_by', 'assigned_to', 'created_at', 'deadline']
        model = Task


class TaskStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'task', 'status', 'comment']
        model = TaskStatus


class TaskEstimationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'deadline_meeting', 'completeness', 'quality']
        model = TaskEstimation


class MeetingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    organizer_name = serializers.CharField(source='organizer.user.username', read_only=True)

    def validate(self, data):
        if data['start_at'] >= data['end_at']:
            raise ValidationError('Meeting beginning must be earlier than end of it...')
        return data

    class Meta:
        fields = ['id', 'organizer_name', 'start_at', 'end_at', 'participants']
        model = Meeting

        extra_kwargs = {
            'participants': {'read_only': True}
        }


class CalendarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'start_at', 'end_at', ]
        model = Calendar
