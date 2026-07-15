"""Forms for account registration and profile management."""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

from .models import UserProfile


class RegistrationForm(UserCreationForm):
    """Public registration form with an email field."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Ensure the email address is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        """Persist the new user and its profile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Editable channel profile settings."""

    class Meta:
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
            "date_of_birth",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class AccountSettingsForm(UserChangeForm):
    """Allow editing of core account fields without password changes."""

    password = None  # Hide the password field from the settings form.

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
