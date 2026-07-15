"""Views for displaying and managing notifications."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    """List the current user's notifications."""
    notifications = request.user.notifications.all()[:50]
    return render(
        request,
        "notifications/list.html",
        {"notifications": notifications},
    )


@login_required
@require_POST
def mark_all_read(request):
    """Mark every notification for the user as read."""
    request.user.notifications.update(is_read=True)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})
    return redirect("notifications:list")


@login_required
@require_POST
def mark_read(request, pk):
    """Mark a single notification as read."""
    Notification.objects.filter(pk=pk, recipient=request.user).update(
        is_read=True
    )
    return redirect("notifications:list")
