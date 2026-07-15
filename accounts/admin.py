"""Admin registration for accounts models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import SavedVideo, Subscription, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline editor for a user's profile."""

    model = UserProfile
    fields = (
        "avatar",
        "banner",
        "bio",
        "location",
        "website",
        "twitter",
        "instagram",
        "youtube",
    )


class CustomUserAdmin(UserAdmin):
    """Extend the default user admin with the profile inline."""

    inlines = [UserProfileInline]


# Re-register User with the extended admin.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for channel subscriptions."""

    list_display = ("subscriber", "channel", "created_at")
    list_filter = ("created_at",)
    search_fields = ("subscriber__username", "channel__username")


@admin.register(SavedVideo)
class SavedVideoAdmin(admin.ModelAdmin):
    """Admin for saved videos."""

    list_display = ("user", "video", "created_at")
    search_fields = ("user__username", "video__title")
