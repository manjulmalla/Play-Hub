"""Admin registration for the comments app."""

from django.contrib import admin

from .models import Comment, Like, Reply


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for moderating comments."""

    list_display = ("user", "video", "text_preview", "like_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "user__username", "video__title")

    def text_preview(self, obj):
        """Show a short preview of the comment text."""
        return obj.text[:60]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    """Admin for replies."""

    list_display = ("user", "comment", "text_preview", "created_at")
    search_fields = ("text", "user__username")

    def text_preview(self, obj):
        """Show a short preview of the reply text."""
        return obj.text[:60]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin for likes."""

    list_display = ("user", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
