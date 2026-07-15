"""Views for account registration, profiles and subscriptions."""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView

from videos.models import Video

from .forms import AccountSettingsForm, RegistrationForm, UserProfileForm
from .models import Subscription, UserProfile

User = get_user_model()


class RegisterView(CreateView):
    """Public user registration."""

    form_class = RegistrationForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        """Notify the user on successful registration."""
        messages.success(self.request, "Account created. You can now log in.")
        return super().form_valid(form)


def profile(request, username):
    """Public channel page for a user."""
    channel_user = get_object_or_404(User, username=username)
    profile_obj = getattr(channel_user, "profile", None)
    videos = (
        Video.objects.filter(uploader=channel_user, status="published")
        .select_related("category", "uploader")
        .order_by("-created_at")
    )
    is_owner = request.user.is_authenticated and request.user == channel_user
    is_subscribed = (
        request.user.is_authenticated
        and Subscription.objects.filter(
            subscriber=request.user, channel=channel_user
        ).exists()
    )
    context = {
        "channel_user": channel_user,
        "profile": profile_obj,
        "videos": videos,
        "is_owner": is_owner,
        "is_subscribed": is_subscribed,
        "subscriber_count": channel_user.subscribers.count(),
        "video_count": videos.count(),
    }
    return render(request, "accounts/profile.html", context)


@login_required
def settings_view(request):
    """Combined profile and account settings page."""
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile_obj
        )
        account_form = AccountSettingsForm(request.POST, instance=request.user)
        if profile_form.is_valid() and account_form.is_valid():
            profile_form.save()
            account_form.save()
            messages.success(request, "Your settings have been saved.")
            return redirect("accounts:settings")
    else:
        profile_form = UserProfileForm(instance=profile_obj)
        account_form = AccountSettingsForm(instance=request.user)

    context = {
        "profile_form": profile_form,
        "account_form": account_form,
    }
    return render(request, "accounts/settings.html", context)


@login_required
@require_POST
def toggle_subscription(request, username):
    """Subscribe to or unsubscribe from a channel."""
    channel_user = get_object_or_404(User, username=username)
    if channel_user == request.user:
        messages.warning(request, "You cannot subscribe to yourself.")
        return redirect("accounts:profile", username=username)

    subscription = Subscription.objects.filter(
        subscriber=request.user, channel=channel_user
    ).first()
    if subscription:
        subscription.delete()
        messages.info(request, f"Unsubscribed from {channel_user.username}.")
    else:
        Subscription.objects.create(subscriber=request.user, channel=channel_user)
        messages.success(request, f"Subscribed to {channel_user.username}.")
    return redirect("accounts:profile", username=username)


@login_required
def saved_videos(request):
    """List the videos a user has bookmarked."""
    saved = (
        request.user.saved_videos.select_related("video", "video__uploader")
        .prefetch_related("video__category")
        .order_by("-created_at")
    )
    videos = [item.video for item in saved]
    return render(request, "accounts/saved_videos.html", {"videos": videos})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Password change view with a themed template."""

    template_name = "auth/password_change.html"
    success_url = reverse_lazy("accounts:settings")

    def form_valid(self, form):
        messages.success(self.request, "Your password was changed successfully.")
        return super().form_valid(form)
