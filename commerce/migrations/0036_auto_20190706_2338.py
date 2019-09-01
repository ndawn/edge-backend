# Generated by Django 2.2.2 on 2019-07-06 20:38

import commerce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0035_auto_20190228_0323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(commerce.models.Cover.dummy), to='commerce.Cover', verbose_name='Обложка'),
        ),
    ]
