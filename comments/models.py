"""Comment, reply and like models for social interaction."""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from videos.models import Video

User = get_user_model()


class Comment(models.Model):
    """A top-level comment left on a video."""

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Generic relation so comments can be liked via the generic Like model.
    likes = GenericRelation(
        "Like",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["video", "-created_at"])]

    def __str__(self):
        return f"{self.user.username}: {self.text[:40]}"

    @property
    def reply_count(self):
        """Return the number of replies to this comment."""
        return self.replies.count()


class Reply(models.Model):
    """A reply to a comment."""

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.user.username}: {self.text[:40]}"


class Like(models.Model):
    """A generic like that can target a video, comment or reply."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ("user", "content_type", "object_id")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.content_type} #{self.object_id}"
