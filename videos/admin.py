"""Admin registration for the videos app."""

from django.contrib import admin

from .models import Video, VideoReport


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin editor for videos."""

    list_display = (
        "title",
        "uploader",
        "category",
        "status",
        "is_featured",
        "view_count",
        "like_count",
        "created_at",
    )
    list_filter = ("status", "is_featured", "category", "created_at")
    search_fields = ("title", "description", "tags", "uploader__username")
    readonly_fields = ("duration", "width", "height", "file_size", "view_count")
    list_editable = ("is_featured", "status")
    actions = ["feature_videos", "unfeature_videos"]

    @admin.action(description="Mark selected videos as featured")
    def feature_videos(self, request, queryset):
        """Feature the selected videos."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} video(s) marked as featured.")

    @admin.action(description="Remove featured flag from selected videos")
    def unfeature_videos(self, request, queryset):
        """Unfeature the selected videos."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} video(s) unfeatured.")


@admin.register(VideoReport)
class VideoReportAdmin(admin.ModelAdmin):
    """Admin for moderating video reports."""

    list_display = ("video", "reporter", "reason", "resolved", "created_at")
    list_filter = ("reason", "resolved", "created_at")
    search_fields = ("video__title", "reporter__username", "description")
    actions = ["mark_resolved", "delete_reported_videos"]

    @admin.action(description="Mark selected reports as resolved")
    def mark_resolved(self, request, queryset):
        """Resolve the selected reports."""
        queryset.update(resolved=True)

    @admin.action(description="Delete the reported videos")
    def delete_reported_videos(self, request, queryset):
        """Remove videos that were reported."""
        videos = Video.objects.filter(reports__in=queryset)
        count = videos.count()
        videos.delete()
        self.message_user(request, f"{count} reported video(s) deleted.")
