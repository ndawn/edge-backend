from rest_framework import serializers
from parsers.models import ParseSession, Mode, Site
from django_celery_results.models import TaskResult


class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = ('id', 'name', 'verbose_names', 'default_source')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = (
            'id',
            'address',
        )


class ParseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParseSession
        fields = ('id', 'started', 'finished', 'status', 'meta', 'item_count')


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = ('id', 'task_id', 'task_name', 'status', 'meta', 'result', 'traceback')
