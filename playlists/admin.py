"""Admin registration for the playlists app."""

from django.contrib import admin

from .models import Playlist, PlaylistVideo


class PlaylistVideoInline(admin.TabularInline):
    """Inline editor for the videos inside a playlist."""

    model = PlaylistVideo
    extra = 1


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    """Admin editor for playlists."""

    list_display = ("title", "owner", "is_public", "updated_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "owner__username")
    inlines = [PlaylistVideoInline]


@admin.register(PlaylistVideo)
class PlaylistVideoAdmin(admin.ModelAdmin):
    """Admin for individual playlist entries."""

    list_display = ("playlist", "video", "order", "added_at")
