# core/admin_utils.py
from django.contrib import admin
from django.db import connection
from django_tenants.utils import get_public_schema_name
from django.conf import settings
from modeltranslation.admin import (
    TranslationAdmin,
    TabbedTranslationAdmin,
    TranslationTabularInline,
    TranslationStackedInline,
)
from django import forms
from .tenant_utils import get_current_tenant

from .tenant_admin import tenant_admin_site
from .public_admin import public_admin_site
import logging

logger = logging.getLogger(__name__)


def safe_register(site, model, admin_class):
    """Register a model safely, checking if it's not already registered."""
    try:
        if model in site._registry:
            site.unregister(model)
        site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        logger.warning(f"Model {model} was already registered, forcing unregister")
        try:
            site.unregister(model)
            site.register(model, admin_class)
        except Exception as e:
            logger.error(f"Failed to register {model}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error registering {model}: {e}")


def register_with_all_sites(model):
    """Decorator to register a model in both default admin and tenant admin."""

    def model_admin_wrapper(admin_class):
        safe_register(admin.site, model, admin_class)
        safe_register(tenant_admin_site, model, admin_class)
        return admin_class

    return model_admin_wrapper


def public_register_from_all_sites(model):
    """Decorator to register a model in both default admin and public admin."""

    def model_admin_wrapper(admin_class):
        safe_register(admin.site, model, admin_class)
        safe_register(public_admin_site, model, admin_class)
        return admin_class

    return model_admin_wrapper


def register_everywhere(model):
    """Decorator to register a model in all 3 admin interfaces."""

    def model_admin_wrapper(admin_class):
        safe_register(admin.site, model, admin_class)
        safe_register(tenant_admin_site, model, admin_class)
        safe_register(public_admin_site, model, admin_class)
        return admin_class

    return model_admin_wrapper


def register_tenant_only(model):
    """Decorator for models only available in client tenants."""

    def model_admin_wrapper(admin_class):
        class TenantAwareAdmin(admin_class):
            def _is_public_schema(self):
                return connection.schema_name == get_public_schema_name()

            def has_module_permission(self, request):
                if self._is_public_schema():
                    return False
                try:
                    return super().has_module_permission(request)
                except Exception:
                    return False

            def has_view_permission(self, request, obj=None):
                if self._is_public_schema():
                    return False
                try:
                    return super().has_view_permission(request, obj)
                except Exception:
                    return False

            def has_add_permission(self, request):
                if self._is_public_schema():
                    return False
                try:
                    return super().has_add_permission(request)
                except Exception:
                    return False

            def has_change_permission(self, request, obj=None):
                if self._is_public_schema():
                    return False
                try:
                    return super().has_change_permission(request, obj)
                except Exception:
                    return False

            def has_delete_permission(self, request, obj=None):
                if self._is_public_schema():
                    return False
                try:
                    return super().has_delete_permission(request, obj)
                except Exception:
                    return False

        safe_register(admin.site, model, TenantAwareAdmin)
        safe_register(tenant_admin_site, model, admin_class)
        return admin_class

    return model_admin_wrapper


def register_public_only(model):
    """Decorator for models only available in the public schema."""

    def model_admin_wrapper(admin_class):
        class PublicOnlyAdmin(admin_class):
            def _is_public_schema(self):
                return connection.schema_name == get_public_schema_name()

            def has_module_permission(self, request):
                if not self._is_public_schema():
                    return False
                return super().has_module_permission(request)

            def has_view_permission(self, request, obj=None):
                if not self._is_public_schema():
                    return False
                return super().has_view_permission(request, obj)

        safe_register(admin.site, model, PublicOnlyAdmin)
        safe_register(public_admin_site, model, admin_class)
        return admin_class

    return model_admin_wrapper


class TenantAwareTranslationAdmin(TranslationAdmin):
    """TranslationAdmin that filters languages by tenant."""

    def get_form(self, request, obj=None, **kwargs):
        tenant = get_current_tenant()
        if tenant and hasattr(tenant, "active_languages") and tenant.active_languages:
            original_languages = settings.LANGUAGES
            settings.LANGUAGES = [
                (code, name)
                for code, name in original_languages
                if code in tenant.active_languages
            ]
            try:
                form = super().get_form(request, obj, **kwargs)
            finally:
                settings.LANGUAGES = original_languages
            return form
        return super().get_form(request, obj, **kwargs)


class TenantAwareTabbedTranslationAdmin(TabbedTranslationAdmin):
    """TabbedTranslationAdmin that filters tabs by tenant."""

    def get_form(self, request, obj=None, **kwargs):
        tenant = get_current_tenant()
        if tenant and hasattr(tenant, "active_languages") and tenant.active_languages:
            original_languages = settings.LANGUAGES
            settings.LANGUAGES = [
                (code, name)
                for code, name in original_languages
                if code in tenant.active_languages
            ]
            try:
                form = super().get_form(request, obj, **kwargs)
            finally:
                settings.LANGUAGES = original_languages
            return form
        return super().get_form(request, obj, **kwargs)

    class Media:
        js = ("modeltranslation/js/tabbed_translation_fields.js",)
        css = {"all": ("modeltranslation/css/tabbed_translation_fields.css",)}


class TenantAwareTranslationTabularInline(TranslationTabularInline):
    """Tabular inline that filters languages by tenant."""

    def get_formset(self, request, obj=None, **kwargs):
        tenant = get_current_tenant()
        if tenant and hasattr(tenant, "active_languages") and tenant.active_languages:
            original_languages = settings.LANGUAGES
            settings.LANGUAGES = [
                (code, name)
                for code, name in original_languages
                if code in tenant.active_languages
            ]
            try:
                formset = super().get_formset(request, obj, **kwargs)
            finally:
                settings.LANGUAGES = original_languages
            return formset
        return super().get_formset(request, obj, **kwargs)


class TenantAwareTranslationStackedInline(TranslationStackedInline):
    """Stacked inline that filters languages by tenant."""

    def get_formset(self, request, obj=None, **kwargs):
        tenant = get_current_tenant()
        if tenant and hasattr(tenant, "active_languages") and tenant.active_languages:
            original_languages = settings.LANGUAGES
            settings.LANGUAGES = [
                (code, name)
                for code, name in original_languages
                if code in tenant.active_languages
            ]
            try:
                formset = super().get_formset(request, obj, **kwargs)
            finally:
                settings.LANGUAGES = original_languages
            return formset
        return super().get_formset(request, obj, **kwargs)
