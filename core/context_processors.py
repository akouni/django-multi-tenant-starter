# core/context_processors.py
"""
Adaptive context processors based on tenant type.
"""

from django.db import connection
from django.conf import settings


def get_current_tenant():
    """Retrieve the current tenant safely."""
    try:
        return getattr(connection, "tenant", None)
    except Exception:
        return None


def tenant_context(request):
    """
    Main context processor that loads the right context based on tenant type.
    """
    context = {}

    tenant = get_current_tenant()
    tenant_type = getattr(tenant, "type", "public") if tenant else "public"

    context["current_tenant"] = tenant
    context["tenant_type"] = tenant_type
    context["tenant_name"] = (
        getattr(tenant, "name", "Starter") if tenant else "Starter"
    )
    context["tenant_schema"] = (
        getattr(tenant, "schema_name", "public") if tenant else "public"
    )

    # Tenant active languages
    if tenant and hasattr(tenant, "active_languages") and tenant.active_languages:
        context["tenant_languages"] = tenant.active_languages
        context["tenant_default_language"] = getattr(
            tenant, "default_language", settings.LANGUAGE_CODE
        )
    else:
        context["tenant_languages"] = [lang[0] for lang in settings.LANGUAGES]
        context["tenant_default_language"] = settings.LANGUAGE_CODE

    try:
        if tenant_type == "client":
            # User stats (if authenticated)
            if request.user.is_authenticated:
                try:
                    from tenant_apps.users.models import CustomUser

                    context["total_users"] = CustomUser.objects.count()
                    context["active_users"] = CustomUser.objects.filter(
                        is_active=True
                    ).count()
                except (ImportError, Exception):
                    pass

            # Tenant-specific config
            context["tenant_config"] = {
                "name": getattr(tenant, "name", ""),
                "business_name": getattr(tenant, "business_name", ""),
                "logo": getattr(tenant, "logo", None),
                "primary_color": getattr(tenant, "primary_color", "#337e16"),
            }

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Error in tenant_context processor: {e}")

    return context


def user_context(request):
    """Context processor for common user information."""
    context = {}

    if request.user.is_authenticated:
        user = request.user
        context["current_user"] = user
        context["user_full_name"] = user.get_full_name() or user.username
        context["user_is_staff"] = user.is_staff
        context["user_is_superuser"] = user.is_superuser

        try:
            if hasattr(user, "profile"):
                profile = user.profile
                context["user_profile"] = profile
                context["user_language"] = profile.language
                context["user_timezone"] = profile.timezone
        except Exception:
            pass

    return context


def settings_context(request):
    """Context processor to expose certain settings to templates."""
    return {
        "DEBUG": settings.DEBUG,
        "LANGUAGES": settings.LANGUAGES,
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "SITE_NAME": getattr(settings, "SITE_NAME", "Starter"),
    }
