"""Views for managing playlists."""

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from videos.models import Video

from .forms import PlaylistForm
from .models import Playlist, PlaylistVideo


@login_required
def my_playlists(request):
    """List the current user's playlists."""
    playlists = Playlist.objects.filter(owner=request.user).order_by(
        "-updated_at"
    )
    return render(
        request, "playlists/list.html", {"playlists": playlists}
    )


def playlist_detail(request, pk):
    """Display a playlist and its videos."""
    playlist = get_object_or_404(Playlist, pk=pk)
    if not playlist.is_public and (
        not request.user.is_authenticated or playlist.owner != request.user
    ):
        return render(request, "playlists/private.html", status=403)

    entries = playlist.videos.select_related("video", "video__uploader").all()
    return render(
        request,
        "playlists/detail.html",
        {"playlist": playlist, "entries": entries},
    )


@login_required
def create_playlist(request):
    """Create a new playlist."""
    if request.method == "POST":
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.owner = request.user
            playlist.save()
            return redirect("playlists:detail", pk=playlist.pk)
    else:
        form = PlaylistForm()
    return render(request, "playlists/create.html", {"form": form})


@login_required
@require_POST
def add_video(request, pk):
    """Add a video to a playlist (owner only)."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    video_id = request.POST.get("video_id") or request.POST.get("video")
    video = get_object_or_404(Video, pk=video_id, status="published")
    order = playlist.videos.count()
    PlaylistVideo.objects.get_or_create(
        playlist=playlist, video=video, defaults={"order": order}
    )
    return redirect("playlists:detail", pk=pk)


@login_required
@require_POST
def remove_video(request, pk):
    """Remove a video from a playlist (owner only)."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    entry = get_object_or_404(
        PlaylistVideo, pk=request.POST.get("entry_id"), playlist=playlist
    )
    entry.delete()
    return redirect("playlists:detail", pk=pk)


@login_required
@require_POST
def reorder_video(request, pk):
    """Reorder a playlist video via an explicit order value."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    entry = get_object_or_404(
        PlaylistVideo, pk=request.POST.get("entry_id"), playlist=playlist
    )
    try:
        new_order = int(request.POST.get("order", entry.order))
    except (TypeError, ValueError):
        new_order = entry.order
    entry.order = new_order
    entry.save()
    return JsonResponse({"ok": True, "order": entry.order})


@login_required
@require_POST
def delete_playlist(request, pk):
    """Delete a playlist owned by the current user."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    playlist.delete()
    return redirect("playlists:my_playlists")
