from rest_framework import serializers

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
    organizer = serializers.CharField(source='', read_only=True)

    class Meta:
        fields = ['id', 'organizer', 'start_at', 'end_at', 'participants']
        model = Meeting


class CalendarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'owner', 'start_at', 'end_at', ]
        model = Calendar
