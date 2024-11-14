import datetime
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


class Exam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='No description provided.')  # Add a default value here
    duration = models.IntegerField(default=60)  # Duration in minutes
    date = models.DateField(default=datetime.date.today)
    available_times = models.JSONField(default=list)  # Stores available time slots (e.g., ["08:00", "10:00"])
    locations = models.ManyToManyField(Location)  # Link to multiple locations

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
        unique_together = ['student', 'selected_date', 'selected_time']  # Ensures no overlapping registrations

    def __str__(self):
        return f"{self.student.username} - {self.exam.name} on {self.selected_date} at {self.selected_time}"
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registered_exam_count = models.IntegerField(default=0)  # Field to track number of exams

    def registered_exams(self):
        # Return a queryset of exams this student has registered for
        return Registration.objects.filter(student=self.user).select_related('exam')

    def update_exam_count(self):
        # Helper method to update the registered exam count
        self.registered_exam_count = self.registered_exams().count()
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Profile"
