"""Admin registration for the history app."""

from django.contrib import admin

from .models import WatchHistory


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    """Admin for watch history records."""

    list_display = ("user", "video", "progress", "completed", "last_watched")
    list_filter = ("completed", "last_watched")
    search_fields = ("user__username", "video__title")
