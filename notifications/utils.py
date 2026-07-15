"""Helper utilities for creating notifications."""

from django.contrib.contenttypes.models import ContentType

from .models import Notification


def notify(recipient, sender, notification_type, text, link="", obj=None):
    """Create a notification, skipping self-notifications.

    ``obj`` may be any model instance; its content type and primary key are
    stored so the notification can be linked to the relevant object later.
    """
    if recipient == sender:
        return None
    content_type = None
    object_id = None
    if obj is not None:
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.pk
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text,
        link=link,
        content_type=content_type,
        object_id=object_id,
    )
