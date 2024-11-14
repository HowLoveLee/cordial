
from django.contrib import admin

from .models import Location, Exam, Registration, StudentProfile

# Register your models here.
admin.site.register(Location)
admin.site.register(Exam)
admin.site.register(Registration)
admin.site.register(StudentProfile)