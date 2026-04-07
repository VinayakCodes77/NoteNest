from django.contrib import admin
from django.urls import path, include
from diary import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('check-username/', views.check_username, name='check_username'),
    path('accounts/', include('django.contrib.auth.urls')),
]
