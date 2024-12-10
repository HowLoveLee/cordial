from django.contrib.auth.models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.views.decorators.http import require_POST
from cordialapp.forms import RegistrationForm, LoginForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Exam, Registration, Location
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone

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
@login_required(login_url='/login/')
def student_dashboard(request):
    profile = request.user.studentprofile  # Access the StudentProfile
    registered_exams = profile.registered_exams()  # Get registered exams
    empty_slots = 3 - profile.registered_exam_count  # Calculate empty slots
    empty_slots_range = range(empty_slots)  # Create a range for the empty slots

    context = {
        'user': request.user,
        'registered_exams': registered_exams,
        'empty_slots': empty_slots,  # Total empty slots
        'empty_slots_range': empty_slots_range,  # Range for iterating empty slots
    }

    return render(request, 'student_dashboard.html', context)

@login_required(login_url='/login/')
def exam_registration_process(request):
    exams = Exam.objects.all()
    if request.method == "POST":
        # Retrieve form data
        exam_id = request.POST.get("exam_id")
        selected_date = request.POST.get("selected_date")
        selected_time = request.POST.get("selected_time")
        location_id = request.POST.get("location_id")

        # Get the selected exam and location
        exam = get_object_or_404(Exam, id=exam_id)
        location = get_object_or_404(Location, id=location_id)

        # Check if the student has available slots
        profile = request.user.studentprofile
        if not profile.has_empty_slots():
            messages.error(request, "You cannot register for more than 3 exams at a time.")
            return render(request, 'exam_registration_process.html', {'exams': exams})

        # Validate and process registration
        try:
            registration = Registration.objects.create(
                student=request.user,
                exam=exam,
                selected_date=selected_date,
                selected_time=selected_time,
                location=location
            )
            registration.save()

            # Increment the registered_exam_count
            profile.registered_exam_count += 1
            profile.save()

            # Redirect to confirmation page with registration details
            return redirect(reverse('exam_registration_confirmation', kwargs={'registration_id': registration.id}))
        except Exception as e:
            return render(request, 'exam_registration_process.html', {
                'exams': exams,
                'error_message': str(e),
            })

    return render(request, 'exam_registration_process.html', {'exams': exams})

@login_required(login_url='/login/')
def get_locations_and_times(request, exam_id):
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        locations = exam.locations.all()  # Get all related locations for the exam
        available_times = exam.available_times  # Get available times

        location_data = [
            {'id': location.id, 'name': location.full_address}
            for location in locations
        ]

        return JsonResponse({
            'locations': location_data,
            'available_times': available_times
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='/login/')
def exam_registration_confirmation(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, student=request.user)
    registration_date_localized = timezone.localtime(registration.registration_date)

    return render(request, 'exam_registration_confirmation.html', {
        'registration': registration,
        'registration_date_localized': registration_date_localized,
    })

@login_required(login_url='/login/')
def cancel_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, student=request.user)
    if request.method == "POST":
        if "confirm_cancel" in request.POST:  # Check if the user confirmed the cancellation
            profile = request.user.studentprofile
            if profile.registered_exam_count > 0:
                profile.registered_exam_count -= 1
                profile.save()
            registration.delete()
        # Redirect to the dashboard regardless of the action
        return redirect('student_dashboard')

    return render(request, 'cancel_registration.html', {'registration': registration})


@login_required(login_url='/login/')
def reschedule_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, student=request.user)
    available_times = registration.exam.available_times  # Fetch available times from the exam

    if request.method == "POST":
        if "confirm_reschedule" in request.POST:  # If user confirms the reschedule
            new_date = request.POST.get("new_date")
            new_time = request.POST.get("new_time")

            if new_time not in available_times:
                messages.error(request, "Selected time is not available.")
                return render(request, 'reschedule_registration.html', {
                    'registration': registration,
                    'available_times': available_times,
                })

            try:
                # Update the registration with the new date and time
                registration.selected_date = new_date
                registration.selected_time = new_time
                registration.clean()  # Validate the updated registration
                registration.save()
                return redirect(reverse('exam_registration_confirmation', kwargs={'registration_id': registration.id}))
            except ValidationError as e:
                messages.error(request, str(e))
        else:  # Redirect to the dashboard if the "Cancel" button is clicked
            return redirect('student_dashboard')

    return render(request, 'reschedule_registration.html', {
        'registration': registration,
        'available_times': available_times,
    })


def restricted_access(request):
    messages.warning(request, 'Session Expired. Please log in again.')
    return redirect('/login/?session_expired=true')

def support_QA(request):
    return render(request, 'support_QA.html')

