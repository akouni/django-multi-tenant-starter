# tenant_apps/users/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import UserProfile, Role


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "location",
            "website",
            "language",
            "timezone",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": _("Tell us about yourself..."),
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("City, Country"),
            }),
            "website": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://",
            }),
            "language": forms.Select(attrs={
                "class": "form-select",
            }),
            "timezone": forms.Select(attrs={
                "class": "form-select",
            }),
        }


class InvitationForm(forms.Form):
    """Form for inviting a new user."""

    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": _("Enter email address"),
        }),
    )
    assigned_role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        label=_("Assign role"),
        empty_label=_("-- Select a role --"),
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )
