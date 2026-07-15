"""URL patterns for the playlists application."""

from django.urls import path

from . import views

app_name = "playlists"

urlpatterns = [
    path("", views.my_playlists, name="my_playlists"),
    path("create/", views.create_playlist, name="create"),
    path("<int:pk>/", views.playlist_detail, name="detail"),
    path("<int:pk>/add/", views.add_video, name="add_video"),
    path("<int:pk>/remove/", views.remove_video, name="remove_video"),
    path("<int:pk>/reorder/", views.reorder_video, name="reorder_video"),
    path("<int:pk>/delete/", views.delete_playlist, name="delete_playlist"),
]
