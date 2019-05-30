import logging

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver
from django.db.models.signals import post_save


logger = logging.getLogger()


TYPE_CHOICES = {
    'previews': 'Предзаказы',
}


STATUS_CHOICES = {
    'pending': 'Ожидается',
    'finished': 'Завершена',
    'interrupted': 'Прервана',
}


class ParseSession(models.Model):
    class Meta:
        verbose_name = 'Сессия загрузки'
        verbose_name_plural = 'Сессии загрузки'

    type = models.CharField(
        choices=TYPE_CHOICES.items(),
        blank=True,
        max_length=8,
        verbose_name='Тип',
    )

    started = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Дата начала загрузки',
    )

    finished = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата конца загрузки',
    )

    status = models.CharField(
        choices=STATUS_CHOICES.items(),
        default='pending',
        blank=True,
        max_length=16,
        verbose_name='Статус',
    )

    meta = JSONField(
        verbose_name='Дополнительные данные',
    )


class ParsedObject(models.Model):
    class Meta:
        verbose_name = 'Загруженный объект'
        verbose_name_plural = 'Загруженные объекты'

    session = models.ForeignKey(
        ParseSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Сессия загрузки',
    )

    task = models.OneToOneField(
        'django_celery_results.TaskResult',
        on_delete=models.CASCADE
    )


@receiver(post_save, sender='django_celery_results.TaskResult')
def create_parsed_object(sender, instance, created, **kwargs):
    if created and (instance is not None) and (instance.task_kwargs is not None):
        ParsedObject.objects.create(session_id=instance.task_kwargs.get('session_id'), task=instance)
