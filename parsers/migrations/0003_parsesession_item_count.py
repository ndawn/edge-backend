# Generated by Django 2.2.2 on 2019-08-08 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0002_auto_20190712_0236'),
    ]

    operations = [
        migrations.AddField(
            model_name='parsesession',
            name='item_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество объектов'),
        ),
    ]
