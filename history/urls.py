"""URL patterns for the history application."""

from django.urls import path

from . import views

app_name = "history"

urlpatterns = [
    path("", views.watch_history, name="watch_history"),
    path("progress/", views.update_progress, name="update_progress"),
    path("clear/", views.clear_history, name="clear_history"),
]
