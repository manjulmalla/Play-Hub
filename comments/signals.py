"""Signal handlers that keep denormalised like counts in sync."""

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Comment, Like, Reply


def _recompute_like_count(instance):
    """Update the denormalised like count for a liked object."""
    model = instance.content_type.model_class()
    if model is None:
        return
    target = model.objects.filter(pk=instance.object_id).first()
    if target is None:
        return
    if hasattr(target, "like_count"):
        target.like_count = Like.objects.filter(
            content_type=instance.content_type, object_id=instance.object_id
        ).count()
        target.save(update_fields=["like_count"])


@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    """Recompute the target's like count when a like is added."""
    if created:
        _recompute_like_count(instance)


@receiver(post_delete, sender=Like)
def like_deleted(sender, instance, **kwargs):
    """Recompute the target's like count when a like is removed."""
    # The content type / object id are still available at this point.
    _recompute_like_count(instance)
