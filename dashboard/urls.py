"""URL patterns for the dashboard application."""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.creator_dashboard, name="creator"),
    path("stats/", views.global_stats, name="stats"),
]
