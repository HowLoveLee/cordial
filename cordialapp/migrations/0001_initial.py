# Generated by Django 5.1.2 on 2024-10-28 18:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('gif_file', models.FileField(upload_to='gifs/', validators=[django.core.validators.FileExtensionValidator(['gif'])])),
            ],
        ),
    ]