"""Forms for the playlists application."""

from django import forms

from .models import Playlist


class PlaylistForm(forms.ModelForm):
    """Create or edit a playlist."""

    class Meta:
        model = Playlist
        fields = ("title", "description", "is_public")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
