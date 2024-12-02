from django.urls import path
from django.contrib import admin
from cordialapp import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login, name='login'),

    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('exam_registration/', views.exam_registration_process, name='exam_registration_process'),
    path('exam_registration_confirmation/<int:registration_id>/', views.exam_registration_confirmation, name='exam_registration_confirmation'),
    path('get_locations/<int:exam_id>/', views.get_locations_and_times, name='get_locations_and_times'),
    path('cancel_registration/<int:registration_id>/', views.cancel_registration, name='cancel_registration'),
    path('reschedule_registration/<int:registration_id>/', views.reschedule_registration, name='reschedule_registration'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),  # Placeholder for the dashboard
    path('QASupport/', views.support_QA, name='support_QA'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
]
