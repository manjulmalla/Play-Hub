"""Views for watch history and playback progress."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from videos.models import Video

from .models import WatchHistory


@login_required
def watch_history(request):
    """Show the user's recently watched videos."""
    history = (
        WatchHistory.objects.filter(user=request.user)
        .select_related("video", "video__uploader")
        .prefetch_related("video__category")
    )
    continue_watching = history.filter(completed=False)
    finished = history.filter(completed=True)
    context = {
        "continue_watching": [h.video for h in continue_watching[:12]],
        "finished": [h.video for h in finished[:12]],
        "all": history,
    }
    return render(request, "history/history.html", context)


@login_required
@require_POST
def update_progress(request):
    """Persist playback progress for resume playback (AJAX)."""
    video_id = request.POST.get("video_id")
    try:
        progress = int(request.POST.get("progress", 0))
    except (TypeError, ValueError):
        progress = 0
    video = Video.objects.filter(pk=video_id, status="published").first()
    if not video:
        return JsonResponse({"ok": False}, status=404)

    history, _ = WatchHistory.objects.get_or_create(
        user=request.user, video=video
    )
    history.progress = progress
    # Mark complete when the viewer reaches the final 5% of the video.
    if video.duration and progress >= video.duration * 0.95:
        history.completed = True
    history.save()
    return JsonResponse({"ok": True, "progress": progress})


@login_required
@require_POST
def clear_history(request):
    """Remove all watch history for the current user."""
    WatchHistory.objects.filter(user=request.user).delete()
    return render(request, "history/history.html", {"cleared": True})
