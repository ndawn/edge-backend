# Generated by Django 2.1.5 on 2019-01-13 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0011_auto_20190114_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='origin_title',
            field=models.CharField(blank=True, default='', max_length=512, null=True, verbose_name='Оригинальное название'),
        ),
        migrations.AlterField(
            model_name='item',
            name='origin_title',
            field=models.CharField(blank=True, default='', max_length=512, null=True, verbose_name='Оригинальное название'),
        ),
    ]
