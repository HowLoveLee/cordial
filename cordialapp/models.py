import datetime

from django.core.validators import FileExtensionValidator
from django.db import models

class Location(models.Model):

    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state}, {self.postal_code}"

    def __str__(self):
        return self.full_address

class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today)
    sits_available = models.IntegerField(default=0)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, default=None)
    gif_file = models.FileField(
        upload_to='gifs/',
        validators=[FileExtensionValidator(['gif'])])

    def __str__(self):
        return self.name

