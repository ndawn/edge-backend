# Generated by Django 2.1.5 on 2019-01-13 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0009_variant_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='bought',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Закупочная цена'),
        ),
    ]
