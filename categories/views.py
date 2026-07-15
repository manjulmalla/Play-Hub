"""Views for browsing categories and their videos."""

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from videos.models import Video

from .models import Category


def category_list(request):
    """Show all categories, featured first."""
    categories = Category.objects.all()
    featured = categories.filter(is_featured=True)
    context = {"categories": categories, "featured": featured}
    return render(request, "categories/list.html", context)


def category_detail(request, slug):
    """List published videos within a category."""
    category = get_object_or_404(Category, slug=slug)
    videos = (
        Video.objects.filter(category=category, status="published")
        .select_related("uploader", "category")
        .prefetch_related("likes")
        .order_by("-created_at")
    )
    paginator = Paginator(videos, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"category": category, "page_obj": page_obj}
    return render(request, "categories/detail.html", context)
