# Generated by Django 2.1.5 on 2019-01-20 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('previews', '0007_auto_20190120_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preview',
            name='midtown_cat_id',
        ),
        migrations.RemoveField(
            model_name='preview',
            name='midtown_comp_cat_id',
        ),
    ]
