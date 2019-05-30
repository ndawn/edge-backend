from rest_framework import serializers
from parsers.models import ParseSession
from django_celery_results.models import TaskResult


class ParseSessionSerializer(serializers.HyperlinkedModelSerializer):
    preview_count = serializers.SerializerMethodField()

    class Meta:
        model = ParseSession
        fields = ('url', 'id', 'started', 'finished', 'status', 'meta', 'preview_count')

    def get_preview_count(self, obj):
        return obj.preview_set.count()


class TaskResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskResult
        fields = ('url', 'id', 'task_id', 'task_name', 'status', 'meta', 'result', 'traceback')
