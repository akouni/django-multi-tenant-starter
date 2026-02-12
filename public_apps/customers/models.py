# public_apps/customers/models.py
import re
import logging
from django.db import models, connection
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin

logger = logging.getLogger(__name__)


class SwissCantons(models.TextChoices):
    AG = "AG", _("Aargau")
    AI = "AI", _("Appenzell Innerrhoden")
    AR = "AR", _("Appenzell Ausserrhoden")
    BE = "BE", _("Bern")
    BL = "BL", _("Basel-Landschaft")
    BS = "BS", _("Basel-Stadt")
    FR = "FR", _("Fribourg")
    GE = "GE", _("Geneva")
    GL = "GL", _("Glarus")
    GR = "GR", _("Graubunden")
    JU = "JU", _("Jura")
    LU = "LU", _("Lucerne")
    NE = "NE", _("Neuchatel")
    NW = "NW", _("Nidwalden")
    OW = "OW", _("Obwalden")
    SG = "SG", _("St. Gallen")
    SH = "SH", _("Schaffhausen")
    SO = "SO", _("Solothurn")
    SZ = "SZ", _("Schwyz")
    TG = "TG", _("Thurgau")
    TI = "TI", _("Ticino")
    UR = "UR", _("Uri")
    VD = "VD", _("Vaud")
    VS = "VS", _("Valais")
    ZG = "ZG", _("Zug")
    ZH = "ZH", _("Zurich")


# Schema names that cannot be used by tenants
RESERVED_SCHEMA_NAMES = [
    "public",
    "shared",
    "default",
    "main",
    "admin",
    "information_schema",
    "pg_catalog",
    "pg_toast",
    "pg_temp",
    "extensions",
    "template0",
    "template1",
    "postgres",
    "test",
    "staging",
    "production",
    "dev",
    "api",
    "auth",
    "static",
    "media",
    "www",
    "mail",
    "ftp",
    "localhost",
    "root",
    "system",
    "null",
    "undefined",
    "true",
    "false",
]


def generate_schema_name(name):
    """
    Generate a valid PostgreSQL schema name from a tenant name.
    - Lowercase, alphanumeric + underscores only
    - Prefixed with 'tenant_'
    - Max 63 characters (PostgreSQL identifier limit)
    """
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    schema_name = f"tenant_{slug}"
    # PostgreSQL identifier limit
    schema_name = schema_name[:63]
    return schema_name


def validate_schema_name(value):
    """Validate that the schema name is acceptable."""
    if value in RESERVED_SCHEMA_NAMES:
        raise ValidationError(
            _("'%(value)s' is a reserved schema name."),
            params={"value": value},
        )
    if not re.match(r"^[a-z][a-z0-9_]*$", value):
        raise ValidationError(
            _("Schema name must start with a letter and contain only "
              "lowercase letters, numbers, and underscores.")
        )


class Client(TenantMixin):
    """
    Tenant model representing an organization/client.
    Each client gets its own PostgreSQL schema.
    """

    class TenantType(models.TextChoices):
        PUBLIC = "public", _("Public")
        CLIENT = "client", _("Client")

    name = models.CharField(
        _("Organization Name"),
        max_length=200,
    )
    type = models.CharField(
        _("Tenant Type"),
        max_length=20,
        choices=TenantType.choices,
        default=TenantType.CLIENT,
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        default="",
    )

    # Contact information
    contact_name = models.CharField(
        _("Contact Name"),
        max_length=200,
        blank=True,
        default="",
    )
    contact_email = models.EmailField(
        _("Contact Email"),
        blank=True,
        default="",
    )
    contact_phone = models.CharField(
        _("Contact Phone"),
        max_length=30,
        blank=True,
        default="",
    )

    # Address
    street = models.CharField(
        _("Street"),
        max_length=255,
        blank=True,
        default="",
    )
    city = models.CharField(
        _("City"),
        max_length=100,
        blank=True,
        default="",
    )
    zip_code = models.CharField(
        _("ZIP Code"),
        max_length=10,
        blank=True,
        default="",
    )
    canton = models.CharField(
        _("Canton"),
        max_length=2,
        choices=SwissCantons.choices,
        blank=True,
        default="",
    )

    # Branding
    logo = models.ImageField(
        _("Logo"),
        upload_to="tenant_logos/",
        blank=True,
        null=True,
    )
    primary_color = models.CharField(
        _("Primary Color"),
        max_length=7,
        default="#337e16",
        help_text=_("Hex color code, e.g. #337e16"),
    )

    # Localization
    default_language = models.CharField(
        _("Default Language"),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )
    active_languages = models.JSONField(
        _("Active Languages"),
        default=list,
        blank=True,
        help_text=_("List of active language codes for this tenant."),
    )

    # Status
    is_active = models.BooleanField(
        _("Active"),
        default=True,
    )

    # Timestamps
    created_on = models.DateTimeField(
        _("Created On"),
        auto_now_add=True,
    )
    updated_on = models.DateTimeField(
        _("Updated On"),
        auto_now=True,
    )

    # django-tenants
    auto_create_schema = False
    auto_drop_schema = True

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.schema_name:
            validate_schema_name(self.schema_name)

    def save(self, *args, **kwargs):
        # Auto-generate schema name if not set
        if not self.schema_name and self.name:
            self.schema_name = generate_schema_name(self.name)

        # Ensure schema name is unique
        if not self.pk and self.schema_name:
            original = self.schema_name
            counter = 1
            while Client.objects.filter(schema_name=self.schema_name).exists():
                self.schema_name = f"{original}_{counter}"
                counter += 1

        # Default active_languages
        if not self.active_languages:
            self.active_languages = [lang[0] for lang in settings.LANGUAGES]

        super().save(*args, **kwargs)

    def create_schema_manually(self):
        """
        Create the tenant schema and run migrations.
        Called after saving the Client instance.
        """
        try:
            logger.info(f"Creating schema for tenant: {self.schema_name}")
            self.create_schema(check_if_exists=True)
            logger.info(f"Running migrations for tenant: {self.schema_name}")
            call_command("migrate_schemas", schema_name=self.schema_name, verbosity=0)
            logger.info(f"Schema {self.schema_name} created and migrated successfully.")
        except Exception as e:
            logger.error(f"Error creating schema for {self.schema_name}: {e}")
            raise

    def activate_tenant(self):
        """Activate the tenant by setting the connection schema."""
        connection.set_schema(self.schema_name)

    def create_tenant_admin(self, email, password=None):
        """
        Create a superuser inside the tenant schema.
        Returns the created user and the password used.
        """
        import secrets

        if not password:
            password = secrets.token_urlsafe(16)

        # Switch to tenant schema
        self.activate_tenant()

        try:
            from tenant_apps.users.models import CustomUser

            username = email.split("@")[0]
            # Ensure unique username within the tenant
            base_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = CustomUser.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            logger.info(
                f"Admin user '{username}' created for tenant '{self.schema_name}'."
            )
            return user, password
        except ImportError:
            # Fallback to default User model
            from django.contrib.auth import get_user_model

            User = get_user_model()
            username = email.split("@")[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            logger.info(
                f"Admin user '{username}' created for tenant '{self.schema_name}'."
            )
            return user, password
        finally:
            # Reset to public schema
            connection.set_schema_to_public()


class Domain(DomainMixin):
    """
    Domain model for tenant routing.
    Each tenant can have multiple domains.
    """

    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")

    def __str__(self):
        return self.domain
