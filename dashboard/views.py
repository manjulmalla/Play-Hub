"""Views for the creator dashboard and global statistics."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.shortcuts import render

from comments.models import Comment
from history.models import WatchHistory
from videos.models import Video

from accounts.models import Subscription, UserProfile
from categories.models import Category


@login_required
def creator_dashboard(request):
    """Show channel statistics for the logged-in creator."""
    videos = Video.objects.filter(uploader=request.user)
    total_videos = videos.count()
    total_views = videos.aggregate(total=Sum("view_count"))["total"] or 0
    total_likes = videos.aggregate(total=Sum("like_count"))["total"] or 0
    subscribers = Subscription.objects.filter(channel=request.user).count()
    comments = Comment.objects.filter(video__uploader=request.user).count()
    storage_bytes = videos.aggregate(total=Sum("file_size"))["total"] or 0

    # Approximate watch time from completed views of this creator's videos.
    watch_seconds = (
        WatchHistory.objects.filter(
            video__uploader=request.user, completed=True
        ).aggregate(total=Sum("video__duration"))["total"]
        or 0
    )

    recent_uploads = videos.order_by("-created_at")[:5]

    context = {
        "total_videos": total_videos,
        "total_views": total_views,
        "total_likes": total_likes,
        "subscribers": subscribers,
        "comments": comments,
        "storage_bytes": storage_bytes,
        "watch_seconds": watch_seconds,
        "recent_uploads": recent_uploads,
    }
    return render(request, "dashboard/creator.html", context)


@user_passes_test(lambda u: u.is_staff)
def global_stats(request):
    """Platform-wide statistics for staff members."""
    total_users = UserProfile.objects.count()
    total_videos = Video.objects.count()
    total_views = Video.objects.aggregate(total=Sum("view_count"))["total"] or 0
    published = Video.objects.filter(status="published").count()
    total_categories = Category.objects.count()
    total_comments = Comment.objects.count()
    total_subscriptions = Subscription.objects.count()

    context = {
        "total_users": total_users,
        "total_videos": total_videos,
        "published_videos": published,
        "total_views": total_views,
        "total_categories": total_categories,
        "total_comments": total_comments,
        "total_subscriptions": total_subscriptions,
    }
    return render(request, "dashboard/stats.html", context)
