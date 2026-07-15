"""Admin registration for the notifications app."""

from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for notifications."""

    list_display = (
        "recipient",
        "sender",
        "notification_type",
        "text",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("text", "recipient__username", "sender__username")
