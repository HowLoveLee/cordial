# Generated by Django 5.1.2 on 2024-10-31 02:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cordialapp', '0002_location_exam_date_exam_sits_available_exam_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='location',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='date',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='sits_available',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
