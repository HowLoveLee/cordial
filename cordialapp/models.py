import datetime

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings  # Import for linking to the Student model (User)

class Location(models.Model):
    name = models.CharField(max_length=50, default='Unknown Campus')  # Campus name
    room_number = models.IntegerField(default=0)  # Room number field with a default value
    building = models.CharField(max_length=1, default='A')  # Building field with a default value
    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state}, {self.postal_code}"

    def __str__(self):
        return f"Room: {self.room_number}, {self.building} Building, {self.full_address}"


def default_available_times():
    return {
        "07:00": 20, "07:30": 20, "08:00": 20, "08:30": 20,
        "09:00": 20, "09:30": 20, "10:00": 20, "10:30": 20,
        "11:00": 20, "11:30": 20, "12:00": 20, "12:30": 20,
        "13:00": 20, "13:30": 20, "14:00": 20, "14:30": 20,
        "15:00": 20, "15:30": 20, "16:00": 20, "16:30": 20,
        "17:00": 20
    }

class Exam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='No description provided.')
    duration = models.IntegerField(default=60)  # Duration in minutes
    date = models.DateField(default=datetime.date.today)
    locations = models.ManyToManyField(Location)
    available_times = models.JSONField(default=default_available_times)

    def available_slots(self, location, time):
        registrations = Registration.objects.filter(exam=self, location=location, selected_time=time)
        return max(self.available_times.get(time, 0) - registrations.count(), 0)

    def __str__(self):
        return self.name


class Registration(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    selected_date = models.DateField()
    selected_time = models.TimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'selected_date', 'selected_time']

    def clean(self):
        if self.exam.available_slots(self.location, self.selected_time) <= 0:
            raise ValidationError(f"No slots available for {self.exam.name} at this time and location.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        str_time = self.selected_time.strftime("%H:%M")
        if str_time in self.exam.available_times and self.exam.available_times[str_time] > 0:
            self.exam.available_times[str_time] -= 1
            self.exam.save()

    def __str__(self):
        return f"{self.student.username} - {self.exam.name} on {self.selected_date} at {self.selected_time}"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registered_exam_count = models.IntegerField(default=0)  # Tracks registered exams
    
    def registered_exams(self):
        return Registration.objects.filter(student=self.user).select_related('exam', 'location')

    def has_empty_slots(self):
        return self.registered_exam_count < 3  # Maximum of 3 exams

    def __str__(self):
        return f"{self.user.username}'s Profile"
    def save(self, *args, **kwargs):
        if self.registered_exam_count > 3:
            raise ValidationError("A student cannot register for more than 3 exams at a time.")
        super().save(*args, **kwargs)