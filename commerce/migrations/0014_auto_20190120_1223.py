# Generated by Django 2.1.5 on 2019-01-20 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0013_auto_20190120_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='cover',
            name='etag',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='ETag'),
        ),
        migrations.AddField(
            model_name='cover',
            name='height',
            field=models.IntegerField(blank=True, null=True, verbose_name='Высота'),
        ),
        migrations.AddField(
            model_name='cover',
            name='original_cover_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL оригинальной обложки'),
        ),
        migrations.AddField(
            model_name='cover',
            name='original_filename',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Оригинальное имя файла'),
        ),
        migrations.AddField(
            model_name='cover',
            name='signature',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Сигнатура'),
        ),
        migrations.AddField(
            model_name='cover',
            name='version',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Версия'),
        ),
        migrations.AddField(
            model_name='cover',
            name='width',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ширина'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='commerce.Cover', verbose_name='Обложка'),
        ),
    ]
