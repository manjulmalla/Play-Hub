"""Seed the default PlayHub categories."""

from django.db import migrations
from django.utils.text import slugify


CATEGORIES = [
    ("Education", "fas fa-graduation-cap", "Learn something new every day."),
    ("Technology", "fas fa-microchip", "The latest in tech and software."),
    ("Gaming", "fas fa-gamepad", "Gameplay, reviews and esports."),
    ("Entertainment", "fas fa-star", "Shows, sketches and fun."),
    ("Music", "fas fa-music", "Songs, albums and live sessions."),
    ("Sports", "fas fa-futbol", "Highlights and analysis."),
    ("News", "fas fa-newspaper", "Current events and reporting."),
    ("Movies", "fas fa-film", "Trailers, reviews and cinema."),
    ("Tutorials", "fas fa-chalkboard-teacher", "Step by step how-to guides."),
    ("Other", "fas fa-ellipsis-h", "Everything that doesn't fit elsewhere."),
]


def create_categories(apps, schema_editor):
    """Insert the default categories."""
    Category = apps.get_model("categories", "Category")
    for name, icon, description in CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "icon": icon,
                "description": description,
            },
        )


def remove_categories(apps, schema_editor):
    """Remove the default categories on reverse migration."""
    Category = apps.get_model("categories", "Category")
    Category.objects.filter(
        name__in=[name for name, _icon, _desc in CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
