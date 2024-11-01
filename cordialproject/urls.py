# cordialproject/urls.py

from django.urls import path
from django.contrib import admin
from cordialapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('admin/', admin.site.urls),
]
