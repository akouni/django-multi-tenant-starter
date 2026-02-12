# public_apps/main/context_processors.py
from django.conf import settings


def site_info(request):
    """Provide the site name from settings to all templates."""
    return {
        "site_name": getattr(settings, "SITE_NAME", "Multi-Tenant Starter"),
    }
