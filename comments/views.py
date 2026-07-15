"""Views for comments, replies and likes."""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from notifications.utils import notify

from videos.models import Video

from .models import Comment, Like, Reply


@login_required
@require_POST
def add_comment(request, slug):
    """Add a comment to a video."""
    video = get_object_or_404(Video, slug=slug, status="published")
    text = request.POST.get("text", "").strip()
    if text:
        comment = Comment.objects.create(
            video=video, user=request.user, text=text
        )
        notify(
            recipient=video.uploader,
            sender=request.user,
            notification_type="comment",
            text=f"{request.user.username} commented on \"{video.title}\".",
            link=video.get_absolute_url(),
            obj=comment,
        )
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "id": comment.id,
                    "text": comment.text,
                    "username": request.user.username,
                }
            )
    return redirect("videos:detail", slug=slug)


@login_required
@require_POST
def edit_comment(request, comment_id):
    """Edit an existing comment authored by the current user."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    text = request.POST.get("text", "").strip()
    if text:
        comment.text = text
        comment.save()
    return redirect("videos:detail", slug=comment.video.slug)


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Delete a comment authored by the current user."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    slug = comment.video.slug
    comment.delete()
    return redirect("videos:detail", slug=slug)


@login_required
@require_POST
def add_reply(request, comment_id):
    """Reply to a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    text = request.POST.get("text", "").strip()
    if text:
        reply = Reply.objects.create(
            comment=comment, user=request.user, text=text
        )
        notify(
            recipient=comment.user,
            sender=request.user,
            notification_type="reply",
            text=f"{request.user.username} replied to your comment.",
            link=comment.video.get_absolute_url(),
            obj=reply,
        )
    return redirect("videos:detail", slug=comment.video.slug)


@login_required
@require_POST
def like_comment(request, comment_id):
    """Toggle a like on a comment and return JSON."""
    comment = get_object_or_404(Comment, id=comment_id)
    ct = ContentType.objects.get_for_model(Comment)
    like, created = Like.objects.get_or_create(
        user=request.user, content_type=ct, object_id=comment.id
    )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        notify(
            recipient=comment.user,
            sender=request.user,
            notification_type="like",
            text=f"{request.user.username} liked your comment.",
            link=comment.video.get_absolute_url(),
            obj=comment,
        )
    comment.refresh_from_db(fields=["like_count"])
    return JsonResponse({"liked": liked, "like_count": comment.like_count})
