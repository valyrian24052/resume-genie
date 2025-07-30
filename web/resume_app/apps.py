"""App configuration for resume app."""

from django.apps import AppConfig


class ResumeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web.resume_app'