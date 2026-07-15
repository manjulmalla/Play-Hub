"""Database models for user accounts and channel subscriptions."""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


def avatar_upload_path(instance, filename):
    """Store avatars organised by user id and date."""
    return f"avatars/user_{instance.user_id}/{filename}"


def banner_upload_path(instance, filename):
    """Store profile banners organised by user id and date."""
    return f"banners/user_{instance.user_id}/{filename}"


class UserProfile(models.Model):
    """Extended profile information for a registered user (channel owner)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        help_text="Profile picture.",
    )
    banner = models.ImageField(
        upload_to=banner_upload_path,
        blank=True,
        null=True,
        help_text="Channel banner image.",
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short biography shown on the profile page.",
    )
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_absolute_url(self):
        """Link to the channel / profile page."""
        return reverse("accounts:profile", kwargs={"username": self.user.username})

    @property
    def subscriber_count(self):
        """Total number of users subscribed to this channel."""
        return self.user.subscribers.count()

    @property
    def subscribers_count(self):
        """Alias used by templates for clarity."""
        return self.subscriber_count


class Subscription(models.Model):
    """A subscription (follow) from one user to another channel."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    channel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        unique_together = ("subscriber", "channel")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subscriber", "channel"]),
        ]

    def __str__(self):
        return f"{self.subscriber.username} -> {self.channel.username}"


class SavedVideo(models.Model):
    """A lightweight bookmark of a video for the "saved" list."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_videos",
    )
    video = models.ForeignKey(
        "videos.Video",
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Saved Video"
        verbose_name_plural = "Saved Videos"
        unique_together = ("user", "video")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.video.title}"
