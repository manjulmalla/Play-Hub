"""Views for browsing, uploading and streaming videos."""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Exists, F, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from categories.models import Category

from comments.models import Comment, Like

from .forms import VideoEditForm, VideoReportForm, VideoUploadForm
from .models import Video, VideoReport
from .utils import (
    ffmpeg_available,
    generate_hls,
    generate_thumbnail,
    probe_metadata,
)


def _annotate_liked(queryset, user):
    """Annotate a video queryset with whether ``user`` has liked each video."""
    if not user.is_authenticated:
        return queryset
    video_ct = ContentType.objects.get_for_model(Video)
    liked = Like.objects.filter(
        user=user, content_type=video_ct, object_id=OuterRef("pk")
    )
    return queryset.annotate(is_liked=Exists(liked))


def home(request):
    """Homepage with featured, trending, latest and personalised sections."""
    featured = Video.objects.published().filter(is_featured=True)[:8]
    trending = Video.objects.published().order_by("-view_count")[:12]
    latest = Video.objects.published().order_by("-created_at")[:12]
    popular_categories = Category.objects.filter(is_featured=True)[:8]

    continue_watching = []
    recommended = []
    if request.user.is_authenticated:
        from history.models import WatchHistory

        continue_watching = [
            wh.video
            for wh in WatchHistory.objects.filter(
                user=request.user, completed=False
            )
            .select_related("video")
            .prefetch_related("video__category")[:8]
        ]
        # Recommend videos from categories the user has watched.
        watched_cats = (
            WatchHistory.objects.filter(user=request.user)
            .values_list("video__category", flat=True)
            .distinct()
        )
        recommended = (
            Video.objects.published()
            .filter(category__in=watched_cats)
            .exclude(pk__in=[v.pk for v in continue_watching])[:12]
        )

    context = {
        "featured": _annotate_liked(featured, request.user),
        "trending": _annotate_liked(trending, request.user),
        "latest": _annotate_liked(latest, request.user),
        "popular_categories": popular_categories,
        "continue_watching": continue_watching,
        "recommended": _annotate_liked(recommended, request.user),
    }
    return render(request, "videos/home.html", context)


def explore(request):
    """Browse all published videos with filtering and sorting."""
    videos = Video.objects.published().select_related("uploader", "category")

    category_slug = request.GET.get("category")
    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    query = request.GET.get("q")
    if query:
        videos = videos.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
        )

    sort = request.GET.get("sort", "newest")
    if sort == "views":
        videos = videos.order_by("-view_count")
    elif sort == "likes":
        videos = videos.order_by("-like_count")
    else:
        videos = videos.order_by("-created_at")

    videos = _annotate_liked(videos, request.user)

    paginator = Paginator(videos, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    context = {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "selected_sort": sort,
        "query": query or "",
    }
    return render(request, "videos/explore.html", context)


def video_detail(request, slug):
    """Play a single video and show its metadata, comments and related videos."""
    video = get_object_or_404(
        Video.objects.published().select_related("uploader", "category"),
        slug=slug,
    )

    # Count a view once per session to avoid inflating the counter.
    viewed_key = f"viewed_{video.pk}"
    if not request.session.get(viewed_key):
        Video.objects.filter(pk=video.pk).update(
            view_count=F("view_count") + 1
        )
        request.session[viewed_key] = True
        request.session.modified = True

    # Record watch history for authenticated users.
    progress = 0
    if request.user.is_authenticated:
        from history.models import WatchHistory

        history, _ = WatchHistory.objects.get_or_create(
            user=request.user, video=video
        )
        progress = history.progress

    is_liked = False
    is_saved = False
    if request.user.is_authenticated:
        video_ct = ContentType.objects.get_for_model(Video)
        is_liked = Like.objects.filter(
            user=request.user, content_type=video_ct, object_id=video.pk
        ).exists()
        is_saved = video.saved_by.filter(user=request.user).exists()

    comments = (
        Comment.objects.filter(video=video)
        .select_related("user")
        .prefetch_related("replies__user", "likes")[:50]
    )

    related = (
        Video.objects.published()
        .exclude(pk=video.pk)
        .filter(category=video.category)
        if video.category
        else Video.objects.published().exclude(pk=video.pk)
    )
    related = _annotate_liked(related.order_by("-view_count")[:12], request.user)

    context = {
        "video": video,
        "comments": comments,
        "related": related,
        "is_liked": is_liked,
        "is_saved": is_saved,
        "progress": progress,
        "report_form": VideoReportForm(),
    }
    return render(request, "videos/detail.html", context)


@login_required
def upload_video(request):
    """Upload a new video and run optional FFmpeg processing."""
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploader = request.user
            video.file_size = request.FILES["video_file"].size
            video.status = "processing"
            video.save()

            _process_uploaded_video(video)

            return redirect("videos:my_videos")
    else:
        form = VideoUploadForm()
    return render(
        request,
        "videos/upload.html",
        {"form": form, "ffmpeg_available": ffmpeg_available()},
    )


def _process_uploaded_video(video):
    """Extract metadata, thumbnail and optional HLS for an uploaded video."""
    # Resolve the absolute path to the stored video file.
    from django.conf import settings

    video_path = str(settings.MEDIA_ROOT / video.video_file.name)

    # Probe metadata (duration / resolution).
    metadata = probe_metadata(video_path)
    if metadata:
        video.duration, video.width, video.height = metadata

    # Generate a thumbnail if the user did not upload one.
    if not video.thumbnail and ffmpeg_available():
        from pathlib import Path

        thumb_name = Path(video.video_file.name).stem + ".jpg"
        thumb_path = settings.MEDIA_ROOT / "thumbnails" / thumb_name
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        if generate_thumbnail(video_path, str(thumb_path)):
            relative = thumb_path.relative_to(settings.MEDIA_ROOT)
            video.thumbnail = str(relative)

    # Optionally build an HLS variant for adaptive streaming.
    if ffmpeg_available():
        from pathlib import Path

        hls_dir = settings.MEDIA_ROOT / "videos" / Path(video.video_file.name).stem
        master = generate_hls(video_path, str(hls_dir))
        if master:
            video.hls_playlist = str(
                Path(master).relative_to(settings.MEDIA_ROOT)
            )

    video.status = "published"
    video.save()


@login_required
def my_videos(request):
    """List the current user's uploaded videos."""
    videos = (
        Video.objects.filter(uploader=request.user)
        .order_by("-created_at")
        .annotate(comment_total=Count("comments"))
    )
    return render(request, "videos/my_videos.html", {"videos": videos})


@login_required
def edit_video(request, slug):
    """Edit metadata for one of the user's videos."""
    video = get_object_or_404(Video, slug=slug, uploader=request.user)
    if request.method == "POST":
        form = VideoEditForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            return redirect("videos:my_videos")
    else:
        form = VideoEditForm(instance=video)
    return render(request, "videos/edit_video.html", {"form": form, "video": video})


@login_required
@require_POST
def delete_video(request, slug):
    """Delete one of the user's videos."""
    video = get_object_or_404(Video, slug=slug, uploader=request.user)
    video.delete()
    return redirect("videos:my_videos")


@login_required
@require_POST
def like_video(request, slug):
    """Toggle the current user's like on a video and return JSON."""
    video = get_object_or_404(Video, slug=slug, status="published")
    video_ct = ContentType.objects.get_for_model(Video)
    like, created = Like.objects.get_or_create(
        user=request.user, content_type=video_ct, object_id=video.pk
    )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Notify the uploader of a new like.
        from notifications.utils import notify

        notify(
            recipient=video.uploader,
            sender=request.user,
            notification_type="like",
            text=f"{request.user.username} liked your video \"{video.title}\".",
            link=video.get_absolute_url(),
            obj=video,
        )
    video.refresh_from_db(fields=["like_count"])
    return JsonResponse(
        {"liked": liked, "like_count": video.like_count}
    )


@login_required
@require_POST
def toggle_save_video(request, slug):
    """Bookmark or un-bookmark a video for the current user."""
    from accounts.models import SavedVideo

    video = get_object_or_404(Video, slug=slug, status="published")
    saved, created = SavedVideo.objects.get_or_create(
        user=request.user, video=video
    )
    if not created:
        saved.delete()
        saved_state = False
    else:
        saved_state = True
    return JsonResponse({"saved": saved_state})


@login_required
def report_video(request, slug):
    """Submit a report against a video."""
    video = get_object_or_404(Video, slug=slug, status="published")
    if request.method == "POST":
        form = VideoReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.video = video
            report.reporter = request.user
            report.save()
            return redirect("videos:detail", slug=slug)
    else:
        form = VideoReportForm()
    return render(
        request, "videos/report.html", {"form": form, "video": video}
    )
