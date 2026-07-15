"""App configuration for the comments application."""

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """Configuration for the comments app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "comments"
    verbose_name = "Comments"

    def ready(self):
        """Import signal handlers when the app is ready."""
        from . import signals  # noqa: F401
