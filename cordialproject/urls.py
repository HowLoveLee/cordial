from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from cordialapp import views

urlpatterns = ([
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('admin/', admin.site.urls),
] )
               # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
