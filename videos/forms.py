"""Forms for uploading and editing videos."""

from django import forms
from django.core.exceptions import ValidationError

from categories.models import Category

from .models import VideoReport, Video

ALLOWED_VIDEO_EXTENSIONS = (".mp4", ".webm", ".mov", ".mkv", ".avi")
MAX_UPLOAD_SIZE = 300 * 1024 * 1024  # 300 MB


def validate_video_file(value):
    """Validate extension and size of an uploaded video file."""
    name = getattr(value, "name", "") or ""
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    if f".{ext}" not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type. Allowed: mp4, webm, mov, mkv, avi."
        )
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError("File is too large (max 300 MB).")


class VideoUploadForm(forms.ModelForm):
    """Form used for the drag & drop upload experience."""

    video_file = forms.FileField(
        label="Video file",
        validators=[validate_video_file],
    )

    class Meta:
        model = Video
        fields = (
            "title",
            "description",
            "category",
            "tags",
            "video_file",
            "thumbnail",
            "allow_comments",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "tags": forms.TextInput(
                attrs={"placeholder": "django, tutorial, python"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Uncategorised"


class VideoEditForm(forms.ModelForm):
    """Form for editing an existing video's metadata."""

    class Meta:
        model = Video
        fields = (
            "title",
            "description",
            "category",
            "tags",
            "thumbnail",
            "allow_comments",
            "is_featured",
            "status",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Uncategorised"


class VideoReportForm(forms.ModelForm):
    """Form for reporting a video."""

    class Meta:
        model = VideoReport
        fields = ("reason", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
