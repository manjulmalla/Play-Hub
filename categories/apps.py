"""App configuration for the categories application."""

from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    """Configuration for the categories app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "categories"
    verbose_name = "Categories"
