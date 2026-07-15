"""URL patterns for the comments application."""

from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("add/<slug:slug>/", views.add_comment, name="add"),
    path("edit/<int:comment_id>/", views.edit_comment, name="edit"),
    path("delete/<int:comment_id>/", views.delete_comment, name="delete"),
    path("reply/<int:comment_id>/", views.add_reply, name="reply"),
    path("like/<int:comment_id>/", views.like_comment, name="like"),
]
