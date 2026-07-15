"""Video and report models for the streaming platform."""

import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


def video_upload_path(instance, filename):
    """Organise uploaded videos by upload date: videos/YYYY/MM/name."""
    now = datetime.now()
    ext = os.path.splitext(filename)[1]
    name = slugify(instance.title) or "video"
    return f"videos/{now.year}/{now.month:02d}/{name}{ext}"


def thumbnail_upload_path(instance, filename):
    """Organise thumbnails by upload date: thumbnails/YYYY/MM/name."""
    now = datetime.now()
    ext = os.path.splitext(filename)[1]
    name = slugify(instance.title) or "thumb"
    return f"thumbnails/{now.year}/{now.month:02d}/{name}{ext}"


def hls_upload_path(instance, filename):
    """Store HLS playlists alongside the video date folder."""
    now = datetime.now()
    name = slugify(instance.title) or "video"
    return f"videos/{now.year}/{now.month:02d}/{name}/master.m3u8"


class VideoQuerySet(models.QuerySet):
    """Custom queryset helpers for the Video model."""

    def published(self):
        """Only return videos that are publicly published."""
        return self.filter(status="published")


class Video(models.Model):
    """A single uploaded video asset with metadata."""

    STATUS_CHOICES = (
        ("processing", "Processing"),
        ("published", "Published"),
        ("draft", "Draft"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, blank=True)
    description = models.TextField(blank=True)
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma separated tags, e.g. django, tutorial, python",
    )
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos",
    )
    video_file = models.FileField(upload_to=video_upload_path)
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        blank=True,
        null=True,
    )
    hls_playlist = models.FileField(
        upload_to=hls_upload_path,
        blank=True,
        null=True,
        help_text="Master HLS playlist path when adaptive streaming is available.",
    )
    duration = models.PositiveIntegerField(
        default=0, help_text="Duration in seconds."
    )
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    file_size = models.PositiveBigIntegerField(default=0, help_text="Bytes.")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="processing"
    )
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VideoQuerySet.as_manager()

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["-view_count"]),
            models.Index(fields=["-like_count"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate a unique slug from the title."""
        if not self.slug:
            base = slugify(self.title) or "video"
            slug = base
            counter = 1
            qs = Video.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.exists():
                slug = f"{base}-{counter}"
                counter += 1
                qs = Video.objects.filter(slug=slug)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Link to the video detail page."""
        return reverse("videos:detail", kwargs={"slug": self.slug})

    @property
    def formatted_duration(self):
        """Return the duration as ``H:MM:SS`` or ``M:SS``."""
        seconds = int(self.duration or 0)
        if seconds <= 0:
            return "0:00"
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @property
    def resolution_label(self):
        """Return a human readable resolution label, e.g. ``720p``."""
        if not self.height:
            return ""
        return f"{self.height}p"

    @property
    def tag_list(self):
        """Return the tags as a Python list."""
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def comment_count(self):
        """Return the number of top-level comments."""
        return self.comments.count()


class VideoReport(models.Model):
    """A user report against an uploaded video."""

    REASON_CHOICES = (
        ("spam", "Spam or misleading"),
        ("violence", "Violent or repulsive"),
        ("hate", "Hateful or abusive"),
        ("sexual", "Sexual content"),
        ("other", "Other"),
    )

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="reports"
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Video Report"
        verbose_name_plural = "Video Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on {self.video.title} ({self.reason})"
