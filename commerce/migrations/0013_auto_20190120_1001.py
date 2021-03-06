# Generated by Django 2.1.5 on 2019-01-20 07:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0012_auto_20190114_0119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cover',
            fields=[
                ('_id', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='ID')),
                ('phash', models.BigIntegerField(blank=True, null=True, verbose_name='pHash')),
            ],
        ),
        migrations.RemoveField(
            model_name='variant',
            name='cover_id',
        ),
        migrations.AddField(
            model_name='variant',
            name='cover',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='commerce.Cover', verbose_name='Обложка'),
        ),
    ]
