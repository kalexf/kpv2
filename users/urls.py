from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
# defautt auth paths
path('',include('django.contrib.auth.urls')),
path('register/', views.register,name='register')
]