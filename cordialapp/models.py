from django.core.validators import FileExtensionValidator
from django.db import models

# Create your models here.

class Exam(models.Model):
    name = models.CharField(max_length=100)
    gif_file = models.FileField(
        upload_to='gifs/',
        validators=[FileExtensionValidator(['gif'])])
    def __str__(self):
        return self.name

