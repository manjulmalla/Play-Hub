"""App configuration for the videos application."""

from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Configuration for the videos app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "videos"
    verbose_name = "Videos"
