"""Django settings for the PlayHub project.

This module centralises configuration. Sensitive values are read from a
``.env`` file when present, falling back to sane development defaults.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project directory.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a `.env` file when available.
load_dotenv(str(BASE_DIR / ".env"))


def _as_bool(value, default):
    """Interpret a string environment value as a boolean."""
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


def _as_list(value, default):
    """Coerce a comma separated environment value into a list."""
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = _as_bool(os.getenv("DEBUG"), True)
ALLOWED_HOSTS = _as_list(
    os.getenv("ALLOWED_HOSTS"),
    ["127.0.0.1", "localhost", "testserver", "0.0.0.0"],
)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "")

# Application definition.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # Natural time / number formatting.
    # Local applications.
    "accounts",
    "categories",
    "videos",
    "playlists",
    "comments",
    "history",
    "notifications",
    "dashboard",
    "search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "streamverse.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "streamverse.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "streamverse.wsgi.application"
ASGI_APPLICATION = "streamverse.asgi.application"

# Database - SQLite as required.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication redirects.
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "videos:home"
LOGOUT_REDIRECT_URL = "videos:home"

AUTH_USER_MODEL = "auth.User"

# Internationalisation.
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files.
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "static_collected"

# Media files (uploaded videos, thumbnails, avatars, banners).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login attempts throttling is left to Django's defaults for simplicity.

# Cache: simple in-memory cache to speed up repeated lookups.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "streamverse",
    }
}

# Maximum upload size (300 MB) enforced at the application layer too.
DATA_UPLOAD_MAX_MEMORY_SIZE = 314_572_800

# Session cookie security in production.
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Required so JS can read it if needed.
X_FRAME_OPTIONS = "SAMEORIGIN"
