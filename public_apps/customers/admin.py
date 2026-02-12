# public_apps/customers/admin.py
from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django import forms

from core.admin_utils import public_register_from_all_sites
from .models import Client, Domain


class ClientAdminForm(forms.ModelForm):
    """Custom form for Client admin with language widget."""

    active_languages = forms.MultipleChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Active Languages"),
        help_text=_("Select languages available to this tenant."),
    )

    class Meta:
        model = Client
        fields = "__all__"


class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1
    fields = ("domain", "is_primary")


@public_register_from_all_sites(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = (
        "name",
        "schema_name",
        "type",
        "contact_email",
        "display_languages",
        "is_active",
        "created_on",
    )
    list_filter = ("type", "is_active", "canton", "created_on")
    search_fields = ("name", "schema_name", "contact_name", "contact_email")
    readonly_fields = ("schema_name", "created_on", "updated_on")
    inlines = [DomainInline]

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "schema_name",
                "type",
                "description",
                "is_active",
            ),
        }),
        (_("Contact Information"), {
            "fields": (
                "contact_name",
                "contact_email",
                "contact_phone",
            ),
        }),
        (_("Address"), {
            "fields": (
                "street",
                "city",
                "zip_code",
                "canton",
            ),
        }),
        (_("Branding"), {
            "fields": (
                "logo",
                "primary_color",
            ),
        }),
        (_("Localization"), {
            "fields": (
                "default_language",
                "active_languages",
            ),
        }),
        (_("Timestamps"), {
            "fields": (
                "created_on",
                "updated_on",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description=_("Languages"))
    def display_languages(self, obj):
        if obj.active_languages:
            lang_dict = dict(settings.LANGUAGES)
            return ", ".join(
                str(lang_dict.get(code, code))
                for code in obj.active_languages
            )
        return "-"


@public_register_from_all_sites(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("domain",)
