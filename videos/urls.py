"""URL patterns for the videos application."""

from django.urls import path

from . import views

app_name = "videos"

urlpatterns = [
    path("", views.home, name="home"),
    path("explore/", views.explore, name="explore"),
    path("upload/", views.upload_video, name="upload"),
    path("my/", views.my_videos, name="my_videos"),
    path("edit/<slug:slug>/", views.edit_video, name="edit"),
    path("delete/<slug:slug>/", views.delete_video, name="delete"),
    path("like/<slug:slug>/", views.like_video, name="like"),
    path("save/<slug:slug>/", views.toggle_save_video, name="save"),
    path("report/<slug:slug>/", views.report_video, name="report"),
    path("watch/<slug:slug>/", views.video_detail, name="detail"),
]
