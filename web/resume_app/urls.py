"""URL patterns for resume app."""

from django.urls import path
from . import views

app_name = 'resume_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_resume, name='generate'),
    path('download/<str:filename>/', views.download_resume, name='download'),
]