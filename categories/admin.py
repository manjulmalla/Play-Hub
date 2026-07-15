"""Admin registration for the categories app."""

from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin editor for categories."""

    list_display = ("name", "slug", "is_featured", "created_at")
    list_filter = ("is_featured",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
