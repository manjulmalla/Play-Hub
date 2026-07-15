"""App configuration for the history application."""

from django.apps import AppConfig


class HistoryConfig(AppConfig):
    """Configuration for the history app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "history"
    verbose_name = "Watch History"
