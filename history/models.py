"""Watch history model for tracking viewing progress."""

from django.contrib.auth import get_user_model
from django.db import models

from videos.models import Video

User = get_user_model()


class WatchHistory(models.Model):
    """Records how far a user has watched a particular video."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watch_history",
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="watch_history",
    )
    progress = models.PositiveIntegerField(
        default=0, help_text="Playback position in seconds."
    )
    completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Watch History"
        verbose_name_plural = "Watch History"
        unique_together = ("user", "video")
        ordering = ["-last_watched"]
        indexes = [models.Index(fields=["user", "-last_watched"])]

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"
