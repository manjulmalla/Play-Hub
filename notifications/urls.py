"""URL patterns for the notifications application."""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("mark-read/<int:pk>/", views.mark_read, name="mark_read"),
]
