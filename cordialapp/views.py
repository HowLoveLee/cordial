from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from cordialapp.forms import RegistrationForm, LoginForm
from cordialapp.models import Registration, Location, Exam


def landing(request):
    return  render(request, 'landing.html')

def login(request):
    if request.method == 'POST':
        if 'registerBtn' in request.POST:
            register_form = RegistrationForm(request.POST)
            login_form = LoginForm()
            if register_form.is_valid():
                first_name = register_form.cleaned_data.get('first_name')
                last_name = register_form.cleaned_data.get('last_name')
                email = register_form.cleaned_data.get('email')
                nshe_id = register_form.cleaned_data.get('nshe_id')
                password = register_form.cleaned_data.get('password')

                if not email.endswith('@student.csn.edu'):
                    messages.error(request, 'Email must end with @student.csn.edu.')
                    return render(request, 'login.html', {'register_form': register_form, 'login_form': login_form})

                username = f"{first_name}{nshe_id}"

                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )

                auth_login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Registration failed. Please correct the errors below.')
        elif 'loginBtn' in request.POST:
            login_form = LoginForm(request.POST)
            register_form = RegistrationForm()
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('student_dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')

    else:
        login_form = LoginForm()
        register_form = RegistrationForm()

    context = {
        'login_form': login_form,
        'register_form': register_form,
    }
    return render(request, 'login.html', context)

@require_POST
def logout_view(request):
    logout(request)
    return redirect('landing')
@login_required(login_url='/login/')  # Redirects to the login page if the user is not logged in
def student_dashboard(request):
    profile = request.user.studentprofile  # Access the StudentProfile
    registered_exams = profile.registered_exams()  # Get the registered exams
    empty_slots = 3 - profile.registered_exam_count  # Calculate empty slots
    empty_slots_range = range(empty_slots)  # Create a range for the empty slots

    context = {
        'user': request.user,
        'registered_exams': registered_exams,
        'empty_slots_range': empty_slots_range,  # Pass the range to the template
    }

    return render(request, 'student_dashboard.html', context)

@login_required(login_url='/login/')
def exam_registration_process(request):
    if request.method == 'POST':
        exam_name = request.POST.get('exam_name')
        exam_date = request.POST.get('exam_date')
        exam_time = request.POST.get('exam_time')

        if not (exam_name and exam_date and exam_time):
            return HttpResponseBadRequest("Incomplete registration details.")

        # Get the Exam object
        try:
            exam = Exam.objects.get(name=exam_name)
        except Exam.DoesNotExist:
            return HttpResponseBadRequest("Exam does not exist.")

        # Create the Registration
        Registration.objects.create(
            student=request.user,
            exam=exam,
            location=exam.locations.first(),  # Assign the first location (customize as needed)
            selected_date=exam_date,
            selected_time=exam_time,
        )

        # Redirect to the student dashboard
        return redirect('student_dashboard')

    # For GET requests, display the registration page
    exams = Exam.objects.prefetch_related('locations').all()
    return render(request, 'exam_registration_process.html', {'exams': exams})

def restricted_access(request):
    messages.warning(request, 'Session Expired. Please log in again.')
    return redirect('/login/?session_expired=true')

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


