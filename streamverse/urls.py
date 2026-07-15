"""URL configuration for the PlayHub project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("categories/", include("categories.urls")),
    path("playlists/", include("playlists.urls")),
    path("comments/", include("comments.urls")),
    path("history/", include("history.urls")),
    path("notifications/", include("notifications.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("search/", include("search.urls")),
    # All video routes (home, explore, watch, upload, ...) live at the root.
    path("", include("videos.urls")),
]

# Serve media files locally during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
