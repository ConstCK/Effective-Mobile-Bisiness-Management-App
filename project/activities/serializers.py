from rest_framework import serializers

from activities.models import News, Task, TaskStatus, TaskEstimation, Meeting


class NewsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'content', 'author']
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

    class Meta:
        fields = ['id', 'organized_by', 'start_at', 'end_at', 'participants']
        model = Meeting


class CalendarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'owner', 'start_at', 'end_at', ]
        model = Meeting
