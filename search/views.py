"""Search across videos, categories and channels."""

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from categories.models import Category

from videos.models import Video

User = get_user_model()


def search(request):
    """Run a search query over videos, channels and categories."""
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")
    sort = request.GET.get("sort", "newest")

    videos = Video.objects.published().select_related("uploader", "category")
    channels = []
    categories = []

    if query:
        videos = videos.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
        )
        channels = (
            User.objects.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
            .exclude(username="admin")[:8]
        )
        categories = Category.objects.filter(name__icontains=query)[:8]

    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    if sort == "views":
        videos = videos.order_by("-view_count")
    elif sort == "likes":
        videos = videos.order_by("-like_count")
    else:
        videos = videos.order_by("-created_at")

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    all_categories = Category.objects.all()
    context = {
        "query": query,
        "page_obj": page_obj,
        "channels": channels,
        "categories": categories,
        "all_categories": all_categories,
        "selected_category": category_slug,
        "selected_sort": sort,
        "result_count": videos.count(),
    }
    return render(request, "search/results.html", context)
