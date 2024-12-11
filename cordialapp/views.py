from django.contrib.auth.models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.views.decorators.http import require_POST
from cordialapp.forms import RegistrationForm, LoginForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Exam, Registration, Location, StudentLog
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
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
                nshe_id = register_form.cleaned_data.get('nshe_id')
                password = nshe_id  # Password is set to the full NSHE ID

                email = f"{nshe_id}@student.csn.edu"

                # Check if the email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'This email is already registered. Please use a different email.')
                    return render(request, 'login.html', {'register_form': register_form, 'login_form': login_form})

                last_four_nshe = nshe_id[-4:]

                username = f"{first_name}{last_four_nshe}"

                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )

                # Send a welcome email
                send_mail(
                    subject="Welcome to the Exam Registration System",
                    message=(
                        f"Hi {first_name},\n\n"
                        f"Welcome to the Exam Registration System! Your account has been successfully created!\n\n"
                        f"Username: {username}\n"
                        f"Best regards,\nExam Registration Team"
                    ),
                    from_email="hostemail@gmail.com",
                    recipient_list=[email],
                    fail_silently=False,
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
    profile = request.user.studentprofile
    registered_exams = profile.registered_exams()
    current_count = registered_exams.count()
    empty_slots = 3 - current_count
    if empty_slots < 0:
        empty_slots = 0

    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Fetch logs for the current user
    all_logs = StudentLog.objects.filter(user=request.user)

    # If there's a search query, filter logs by action or details
    if search_query:
        all_logs = all_logs.filter(Q(details__icontains=search_query) | Q(action__icontains=search_query))
    
    # Limit to the first 10 logs after filtering
    logs = all_logs.order_by('-timestamp')[:10]

    context = {
        'user': request.user,
        'registered_exams': registered_exams,
        'empty_slots': empty_slots,
        'empty_slots_range': range(empty_slots),
        'logs': logs,
        'search_query': search_query,
    }

    return render(request, 'student_dashboard.html', context)


@login_required(login_url='/login/')
def exam_registration_process(request):
    profile = request.user.studentprofile
    # Get a list of exam IDs the user is already registered for
    registered_exam_ids = profile.registered_exams().values_list('exam_id', flat=True)
    # Exclude these exam IDs from the available exams
    exams = Exam.objects.exclude(pk__in=registered_exam_ids)
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
            profile.registered_exam_count += 1
            profile.save()

            # Log the registration action
            StudentLog.objects.create(
                user=request.user,
                action='REGISTER',
                details=f"Exam: {exam.name}, Date: {selected_date}, Time: {selected_time}, Location: {location.full_address}"
            )

            # Send confirmation email
            send_mail(
                subject="Exam Registration Confirmation",
                message=(
                    f"Hi {request.user.first_name}, \n\n"
                    f"You have successfully registered for the exam: \n\n"
                    f"Exam: {exam.name}\n"
                    f"Date: {selected_date} \n"
                    f"Time: {selected_time} \n"
                    f"Location: {location.name}\n\n"
                    f"Best Regards,\nCSN Exam Registration Team - CA"
                ),
                from_email="hostemail@gmail.com",
                recipient_list=[request.user.email],
                fail_silently=False,
            )

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

    context = {
        'registration': registration,
        'registration_date_localized': registration_date_localized,
        'reschedule_url': reverse('reschedule_registration', kwargs={'registration_id': registration_id}),
        'cancel_url': reverse('cancel_registration', kwargs={'registration_id': registration_id}),
        'confirm_url': reverse('student_dashboard'),
    }

    return render(request, 'exam_registration_confirmation.html', context)

@login_required(login_url='/login/')
def cancel_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, student=request.user)
    if request.method == "POST":
        if "confirm_cancel" in request.POST:  # Check if the user confirmed the cancellation
            profile = request.user.studentprofile
            if profile.registered_exam_count > 0:
                profile.registered_exam_count -= 1
                profile.save()

                StudentLog.objects.create(
                    user=request.user,
                    action='CANCEL',
                    details=f"Cancelled Exam: {registration.exam.name} originally scheduled on {registration.selected_date} at {registration.selected_time}"
                )

                # Send cancellation email
                send_mail(
                    subject="Exam Cancellation Confirmation",
                    message=(
                        f"Hi {request.user.first_name}, \n\n"
                        f"You have successfully cancelled your exam: \n\n"
                        f"Exam: {registration.exam.name}\n"
                        f"Originally scheduled for: {registration.selected_date} at {registration.selected_time}\n\n"
                        f"Best Regards,\nCSN Exam Registration Team - CA"
                    ),
                    from_email="hostemail@gmail.com",
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                registration.delete()
        # Redirect to the dashboard regardless of the action
        return redirect('student_dashboard')

    return render(request, 'cancel_registration.html', {'registration': registration})



login_required(login_url='/login/')
def reschedule_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, student=request.user)
    available_times = registration.exam.available_times  # Fetch available times from the exam

    if request.method == "POST":
        if "confirm_reschedule" in request.POST:
            new_date = request.POST.get("new_date")
            new_time = request.POST.get("new_time")

            # Capture old date/time before updating
            old_date = registration.selected_date
            old_time = registration.selected_time

            # Check if the new time is available
            if new_time not in available_times:
                messages.error(request, "Selected time is not available.")
                return render(request, 'reschedule_registration.html', {
                    'registration': registration,
                    'available_times': available_times,
                })

            # Update the registration with the new date and time
            registration.selected_date = new_date
            registration.selected_time = new_time

            try:
                registration.clean()  # Validate the updated registration
                registration.save()

                # Log the reschedule action
                StudentLog.objects.create(
                    user=request.user,
                    action='RESCHEDULE',
                    details=(f"Rescheduled Exam: {registration.exam.name} from {old_date} {old_time} "
                             f"to {new_date} {new_time}")
                )

                # Send reschedule confirmation email
                send_mail(
                    subject="Exam Reschedule Confirmation",
                    message=(
                        f"Hi {request.user.first_name}, \n\n"
                        f"You have successfully rescheduled your exam: \n\n"
                        f"Exam: {registration.exam.name}\n"
                        f"New schedule: {new_date} at {new_time}\n"
                        f"Previous schedule: {old_date} at {old_time}\n\n"
                        f"Best,\nCordial Associtates - CA"
                    ),
                    from_email="hostemail@gmail.com",
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                return redirect(reverse('exam_registration_confirmation', kwargs={'registration_id': registration.id}))
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            return redirect('student_dashboard')

    return render(request, 'reschedule_registration.html', {
        'registration': registration,
        'available_times': available_times,
    })



@login_required(login_url='/login/')
def student_logs_view(request):
    # Fetch all logs for the current user
    all_logs = StudentLog.objects.filter(user=request.user)

    # Setup pagination for 10 logs per page
    paginator = Paginator(all_logs, 10)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    return render(request, 'student_logs.html', {'logs': logs_page})
def restricted_access(request):
    messages.warning(request, 'Session Expired. Please log in again.')
    return redirect('/login/?session_expired=true')

def support_QA(request):
    return render(request, 'support_QA.html')

from django.db.models import Q

@login_required(login_url='/login/')
def teacher_report_view(request):
    if not request.user.has_perm('cordialapp.teacher_view'):
        return render(request, 'no_access.html', status=403)

    student_name = request.GET.get('student_name', '')
    exam_name = request.GET.get('exam_name', '')
    exam_date = request.GET.get('exam_date', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    qs = Registration.objects.select_related('exam', 'location', 'student__studentprofile', 'student')

    if student_name:
        qs = qs.filter(student__first_name__icontains=student_name) | qs.filter(student__last_name__icontains=student_name)
    if exam_name:
        qs = qs.filter(exam__name__icontains=exam_name)
    if exam_date:
        qs = qs.filter(selected_date=exam_date)
    if search_query:
        qs = qs.filter(Q(student__username__icontains=search_query) | 
                       Q(exam__name__icontains=search_query) |
                       Q(location__name__icontains=search_query))

    # Now qs is filtered according to the parameters
    registrations = qs.order_by('exam__name', 'selected_date')

    return render(request, 'teacher_report.html', {
        'registrations': registrations,
        'student_name': student_name,
        'exam_name': exam_name,
        'exam_date': exam_date,
        'search_query': search_query,
    })


@login_required(login_url='/login/')
def student_history(request):
    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Fetch logs for the current user
    all_logs = StudentLog.objects.filter(user=request.user)

    # If there's a search query, filter logs by action or details
    if search_query:
        all_logs = all_logs.filter(Q(details__icontains=search_query) | Q(action__icontains=search_query))
    
    # Limit to the first 10 logs after filtering
    logs = all_logs.order_by('-timestamp')[:10]

    context = {
        'logs': logs,
        'search_query': search_query,
    }

    return render(request, 'student_history.html', context)


@login_required(login_url='/login/')
def student_info(request):
    context = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'password': 'NSHE ID is the password'  # Do not expose actual passwords
    }

    return render(request, 'student_info.html', context)