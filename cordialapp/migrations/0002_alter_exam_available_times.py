# Generated by Django 5.1.3 on 2024-12-11 11:49

import cordialapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cordialapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='available_times',
            field=models.JSONField(default=cordialapp.models.default_available_times),
        ),
    ]
