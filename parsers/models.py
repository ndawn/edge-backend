import logging
import ast

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


class Site(models.Model):
    class Meta:
        verbose_name = 'Адрес сайта'
        verbose_name_plural = 'Адреса сайтов'

    address = models.CharField(
        unique=True,
        max_length=32,
        verbose_name='Имя хоста',
    )

    def __str__(self):
        return self.address


class Mode(models.Model):
    class Meta:
        verbose_name = 'Режим загрузки'
        verbose_name_plural = 'Режимы загрузки'

    name = models.CharField(
        default='',
        max_length=32,
        verbose_name='Название',
    )

    default_source = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Источник по умолчанию',
    )


class ParseSession(models.Model):
    class Meta:
        verbose_name = 'Сессия загрузки'
        verbose_name_plural = 'Сессии загрузки'

    type = models.CharField(
        choices=list(TYPE_CHOICES.items()),
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
        choices=list(STATUS_CHOICES.items()),
        default='pending',
        blank=True,
        max_length=16,
        verbose_name='Статус',
    )

    item_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Количество объектов',
    )

    meta = JSONField(
        default=dict,
        verbose_name='Дополнительные данные',
    )

    def ready(self):
        return self.status == 'finished'


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
        ParsedObject.objects.create(session_id=ast.literal_eval(instance.task_kwargs).get('session_id'), task=instance)
