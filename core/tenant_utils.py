# core/tenant_utils.py - Utilities for tenant management
from django.db import connection
import logging

logger = logging.getLogger(__name__)


def get_current_tenant():
    """
    Retrieve the current tenant safely.
    Compatible with all versions of django-tenants.
    """
    try:
        # Method 1: Via connection.tenant (django-tenants >= 3.0)
        if hasattr(connection, "tenant") and connection.tenant:
            return connection.tenant

        # Method 2: Via get_tenant() if available
        if hasattr(connection, "get_tenant"):
            return connection.get_tenant()

        # Method 3: Via connection.schema_name (fallback)
        elif hasattr(connection, "schema_name"):
            schema_name = connection.schema_name

            if schema_name == "public":
                from types import SimpleNamespace

                return SimpleNamespace(
                    type="public", schema_name="public", name="Public Schema"
                )
            else:
                try:
                    from public_apps.customers.models import Client

                    return Client.objects.get(schema_name=schema_name)
                except Exception as e:
                    logger.warning(
                        f"Could not retrieve tenant {schema_name}: {e}"
                    )
                    from types import SimpleNamespace

                    return SimpleNamespace(
                        type="client",
                        schema_name=schema_name,
                        name=f"Client {schema_name}",
                    )

        logger.warning("No method available to retrieve current tenant")
        return None

    except Exception as e:
        logger.error(f"Error retrieving tenant: {e}")
        return None


def get_tenant_type():
    """Get the current tenant type"""
    tenant = get_current_tenant()
    return getattr(tenant, "type", None) if tenant else None


def get_schema_name():
    """Get the current schema name"""
    try:
        if hasattr(connection, "schema_name"):
            return connection.schema_name

        tenant = get_current_tenant()
        return getattr(tenant, "schema_name", None) if tenant else None

    except Exception as e:
        logger.error(f"Error getting schema_name: {e}")
        return None


def is_public_schema():
    """Check if we're in the public schema"""
    schema_name = get_schema_name()
    return schema_name == "public"


def is_client_schema():
    """Check if we're in a client schema"""
    schema_name = get_schema_name()
    return schema_name and schema_name != "public"


def tenant_type_required(*allowed_types):
    """Decorator to restrict access by tenant type"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            tenant_type = get_tenant_type()
            if tenant_type not in allowed_types:
                from django.core.exceptions import PermissionDenied

                raise PermissionDenied(f"Access denied for tenant type: {tenant_type}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class TenantContextManager:
    """Context manager to ensure a valid tenant exists"""

    def __enter__(self):
        self.tenant = get_current_tenant()
        if not self.tenant:
            raise RuntimeError("No tenant context available")
        return self.tenant

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
