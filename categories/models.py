"""Category model for organising videos into topics."""

from django.db import models
from django.urls import reverse


class Category(models.Model):
    """A top level topic such as Education, Technology, Gaming, etc."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    # Free-form icon class (e.g. a Font Awesome class) for the UI.
    icon = models.CharField(max_length=50, blank=True, default="fas fa-film")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Link to the category listing page."""
        return reverse("categories:detail", kwargs={"slug": self.slug})
