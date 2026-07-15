"""Template tags for exposing notification data to templates."""

from django import template

register = template.Library()


@register.simple_tag
def unread_notifications(user):
    """Return the number of unread notifications for the user."""
    if not user.is_authenticated:
        return 0
    return user.notifications.filter(is_read=False).count()


@register.simple_tag
def recent_notifications(user, limit=5):
    """Return the most recent notifications for the user."""
    if not user.is_authenticated:
        return []
    return user.notifications.all()[:limit]
