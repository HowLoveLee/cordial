from django.shortcuts import render
from .models import Exam

def landing(request):
    return  render(request, 'landing.html')

def login(request):
    return render(request, 'login.html')

def student_dashboard(request):
    return render(request, 'student_dashboard.html')

def exam_registration_process(request):
    return render(request, 'exam_registration_process.html')

def support_QA(request):
    return render(request, 'support_QA.html')

# Landing Page: Welcome Page, Simple branding
# Login/Register Page: This page will login the student into the system or register them.
#   Successful registration will send an email.
# Student Dashboard: This is next after login, student tools for registration.
#   And give the student the ability to schedule, drop, reschedule,
#   show available slots and taken slots. Maximum of 3 exams allowed per student.
# Exam List Page: Display options, I was thinking we use django to populate these slots automatically
#   Vertical list of randomized background colors for divisions. Give the person a list.
# Location Selection Page: Display the 3 campuses next to eacother in pillar format.
# Date and time Selection: Upon selecting time and date
# Confirmation Page, Overview of all the current selected information.
#   Location, Exam name, Exam date and time: Schedule or Cancel.
#   give them ability to give them formatted print. Can go back to dashboard.
#   Sends them back an email for confirmation.
# -------------------------------------------
#          Calculated pages: 7 pages.
# Landing
# Login/Registration
# Student-Dashboard
# Exam-List-Page
#     We might be able to make all these 3 into 1 with dynamic loading.
    # Location-Selection
    # Date and Time Selection
    # Confirmation-Page
# Support and contact Page.
# Adminstration side:
# Django  takes care of them.
# Technologies:
# Django, Nginx, Gunicorn, Some sort of free email system, try gmail. but i remember seeing one
# that allowed up to 50 emails a month.


