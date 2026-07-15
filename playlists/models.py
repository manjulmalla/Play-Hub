"""Playlist and playlist membership models."""

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from videos.models import Video

User = get_user_model()


class Playlist(models.Model):
    """An ordered collection of videos owned by a user."""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="playlists",
    )
    is_public = models.BooleanField(default=True)
    cover = models.ImageField(upload_to="playlists/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Link to the playlist detail page."""
        return reverse("playlists:detail", kwargs={"pk": self.pk})

    @property
    def video_count(self):
        """Return the number of videos in the playlist."""
        return self.videos.count()

    @property
    def total_duration(self):
        """Sum of the durations of all videos in the playlist."""
        return sum(self.videos.values_list("video__duration", flat=True))


class PlaylistVideo(models.Model):
    """A video that belongs to a playlist, with ordering."""

    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="playlist_entries",
    )
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Playlist Video"
        verbose_name_plural = "Playlist Videos"
        ordering = ["order", "added_at"]
        unique_together = ("playlist", "video")

    def __str__(self):
        return f"{self.playlist.title} <- {self.video.title}"
