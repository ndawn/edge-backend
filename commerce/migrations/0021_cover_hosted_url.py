# Generated by Django 2.1.5 on 2019-01-28 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0020_auto_20190129_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='cover',
            name='hosted_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL на стороннем ресурсе'),
        ),
    ]
