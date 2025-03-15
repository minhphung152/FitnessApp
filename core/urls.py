from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import custom_login, CustomLogoutView

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]