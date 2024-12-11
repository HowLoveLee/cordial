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
    selected_time = models.CharField(max_length=5)  # Storing times as strings like "10:30"
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
                
    class Meta:
        unique_together = ['student', 'selected_date', 'selected_time']
        permissions = [
            ("teacher_view", "Can view registrations for reporting purposes"),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep track of the original time slot to detect changes during reschedule
        self._original_time = self.selected_time

    def clean(self):
        if self.exam.available_slots(self.location, self.selected_time) <= 0:
            raise ValidationError(f"No slots available for {self.exam.name} at this time and location.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # If this is a new registration, decrement the slot of the chosen time
        if is_new:
            str_time = self.selected_time
            if str_time in self.exam.available_times and self.exam.available_times[str_time] > 0:
                self.exam.available_times[str_time] -= 1
                self.exam.save()
        else:
            # If the time changed (rescheduling), we need to adjust slots:
            if self.selected_time != self._original_time:
                old_time = self._original_time
                new_time = self.selected_time

                # Return slot to the old time
                if old_time in self.exam.available_times:
                    self.exam.available_times[old_time] += 1

                # Decrement from the new time
                if new_time in self.exam.available_times and self.exam.available_times[new_time] > 0:
                    self.exam.available_times[new_time] -= 1

                self.exam.save()

        # Update the original time reference after saving
        self._original_time = self.selected_time

    def delete(self, *args, **kwargs):
        # When canceling, return a slot to the time slot
        str_time = self.selected_time
        if str_time in self.exam.available_times:
            self.exam.available_times[str_time] += 1
            self.exam.save()
        super().delete(*args, **kwargs)

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
        
        
        
from django.db import models
from django.conf import settings
from django.utils import timezone

class StudentLog(models.Model):
    ACTION_CHOICES = [
        ('REGISTER', 'Registered for Exam'),
        ('CANCEL', 'Cancelled Registration'),
        ('RESCHEDULE', 'Rescheduled Exam'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.timestamp}"
