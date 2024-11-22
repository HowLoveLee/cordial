from django.urls import path
from django.contrib import admin
from cordialapp import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login, name='login'),

    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('exam_registration/', views.exam_registration_process, name='exam_registration_process'),
    path('QASupport/', views.support_QA, name='support_QA'),
    path('logout/', views.logout_view, name='logout'),  # Add this line for logout

    path('admin/', admin.site.urls),
]
