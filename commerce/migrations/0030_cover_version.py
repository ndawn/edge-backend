# Generated by Django 2.1.5 on 2019-02-06 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0029_remove_cover_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='cover',
            name='version',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Версия'),
        ),
    ]
