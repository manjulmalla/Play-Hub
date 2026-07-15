"""App configuration for the playlists application."""

from django.apps import AppConfig


class PlaylistsConfig(AppConfig):
    """Configuration for the playlists app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "playlists"
    verbose_name = "Playlists"
