# Generated by Django 2.1.5 on 2019-01-28 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0021_cover_hosted_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='load_monthly',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='load_weekly',
        ),
        migrations.AddField(
            model_name='publisher',
            name='default_monthly',
            field=models.BooleanField(blank=True, default=True, verbose_name='Месячный по умолчанию'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='default_weekly',
            field=models.BooleanField(blank=True, default=True, verbose_name='Недельный по умолчанию'),
        ),
    ]
