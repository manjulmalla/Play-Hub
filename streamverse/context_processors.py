"""Context processors for PlayHub templates."""

from django.conf import settings
from django.core.cache import cache

from categories.models import Category


def site_settings(request):
    """Expose a handful of site-wide values to every template."""
    categories_list = cache.get("sidebar_categories")
    if categories_list is None:
        categories_list = list(Category.objects.all()[:12])
        cache.set("sidebar_categories", categories_list, 600)
    return {
        "SITE_NAME": "PlayHub",
        "DEBUG": settings.DEBUG,
        "FFMPEG_AVAILABLE": _ffmpeg_available(),
        "categories_list": categories_list,
    }


def _ffmpeg_available():
    """Return True when FFmpeg is usable on this system."""
    from videos.utils import ffmpeg_available

    return ffmpeg_available()
