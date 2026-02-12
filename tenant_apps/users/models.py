# tenant_apps/users/models.py
# Adapted from PaperPoint users/models.py for the multi-tenant starter.

import uuid
import secrets
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tenant_apps.geomap.models import TimeStampedModel


# ==========================================
# UTILITY FUNCTIONS
# ==========================================


def get_user_language(user):
    """Return the preferred language for a user."""
    if hasattr(user, "profile") and user.profile and user.profile.language:
        return user.profile.language
    return settings.LANGUAGE_CODE


def get_user_timezone(user):
    """Return the preferred timezone for a user."""
    if hasattr(user, "profile") and user.profile and user.profile.timezone:
        return user.profile.timezone
    return settings.TIME_ZONE


def get_user_display_name(user):
    """Return the best display name for a user."""
    if user.get_full_name():
        return user.get_full_name()
    return user.username


def get_user_avatar_url(user):
    """Return the avatar URL for a user, or None."""
    if hasattr(user, "avatar") and user.avatar:
        return user.avatar.url
    return None


def generate_invitation_code(length=32):
    """Generate a cryptographically secure invitation code."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_signup_code(length=12):
    """Generate a short signup code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ==========================================
# CUSTOM USER MODEL
# ==========================================


class CustomUser(AbstractUser):
    """Extended user model with additional fields for multi-tenant system."""

    phone = models.CharField(
        _("phone number"),
        max_length=30,
        blank=True,
        default="",
    )
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    is_email_verified = models.BooleanField(
        _("email verified"),
        default=False,
    )
    department = models.CharField(
        _("department"),
        max_length=100,
        blank=True,
        default="",
    )
    job_title = models.CharField(
        _("job title"),
        max_length=100,
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    # Override groups and user_permissions with custom related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username

    def get_display_name(self):
        """Return the best display name."""
        return get_user_display_name(self)


# ==========================================
# ROLE MODEL
# ==========================================


class Role(models.Model):
    """Defines roles within a tenant with associated permissions."""

    DEFAULT_ROLES = [
        ("admin", _("Administrator")),
        ("manager", _("Manager")),
        ("editor", _("Editor")),
        ("viewer", _("Viewer")),
        ("member", _("Member")),
    ]

    HIERARCHY_LEVELS = {
        "admin": 100,
        "manager": 80,
        "editor": 60,
        "viewer": 40,
        "member": 20,
    }

    name = models.CharField(_("role name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True, default="")
    hierarchy_level = models.IntegerField(
        _("hierarchy level"),
        default=0,
        help_text=_("Higher values indicate higher authority."),
    )
    is_default = models.BooleanField(
        _("is default"),
        default=False,
        help_text=_("Whether this role is assigned to new users by default."),
    )

    # Permission booleans
    can_manage_users = models.BooleanField(_("can manage users"), default=False)
    can_manage_roles = models.BooleanField(_("can manage roles"), default=False)
    can_manage_settings = models.BooleanField(_("can manage settings"), default=False)
    can_manage_content = models.BooleanField(_("can manage content"), default=False)
    can_view_reports = models.BooleanField(_("can view reports"), default=False)
    can_export_data = models.BooleanField(_("can export data"), default=False)
    can_invite_users = models.BooleanField(_("can invite users"), default=False)
    can_delete_content = models.BooleanField(_("can delete content"), default=False)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ["-hierarchy_level"]

    def __str__(self):
        return self.name

    @classmethod
    def create_default_roles(cls):
        """Create the default set of roles for a new tenant."""
        defaults = {
            "admin": {
                "description": "Full access to all features and settings.",
                "hierarchy_level": cls.HIERARCHY_LEVELS["admin"],
                "can_manage_users": True,
                "can_manage_roles": True,
                "can_manage_settings": True,
                "can_manage_content": True,
                "can_view_reports": True,
                "can_export_data": True,
                "can_invite_users": True,
                "can_delete_content": True,
            },
            "manager": {
                "description": "Can manage users and content, but not roles or settings.",
                "hierarchy_level": cls.HIERARCHY_LEVELS["manager"],
                "can_manage_users": True,
                "can_manage_roles": False,
                "can_manage_settings": False,
                "can_manage_content": True,
                "can_view_reports": True,
                "can_export_data": True,
                "can_invite_users": True,
                "can_delete_content": True,
            },
            "editor": {
                "description": "Can create and edit content.",
                "hierarchy_level": cls.HIERARCHY_LEVELS["editor"],
                "can_manage_users": False,
                "can_manage_roles": False,
                "can_manage_settings": False,
                "can_manage_content": True,
                "can_view_reports": True,
                "can_export_data": False,
                "can_invite_users": False,
                "can_delete_content": False,
            },
            "viewer": {
                "description": "Read-only access to content.",
                "hierarchy_level": cls.HIERARCHY_LEVELS["viewer"],
                "can_manage_users": False,
                "can_manage_roles": False,
                "can_manage_settings": False,
                "can_manage_content": False,
                "can_view_reports": True,
                "can_export_data": False,
                "can_invite_users": False,
                "can_delete_content": False,
            },
            "member": {
                "description": "Basic member with minimal access.",
                "hierarchy_level": cls.HIERARCHY_LEVELS["member"],
                "is_default": True,
                "can_manage_users": False,
                "can_manage_roles": False,
                "can_manage_settings": False,
                "can_manage_content": False,
                "can_view_reports": False,
                "can_export_data": False,
                "can_invite_users": False,
                "can_delete_content": False,
            },
        }
        created_roles = []
        for role_slug, role_data in defaults.items():
            role_name = dict(cls.DEFAULT_ROLES).get(role_slug, role_slug.title())
            role, created = cls.objects.get_or_create(
                slug=role_slug,
                defaults={"name": str(role_name), **role_data},
            )
            if created:
                created_roles.append(role)
        return created_roles


# ==========================================
# USER PROFILE
# ==========================================


class UserProfile(models.Model):
    """Extended profile for a CustomUser. One-to-one relationship."""

    LANGUAGE_CHOICES = [
        ("en", _("English")),
        ("fr", _("French")),
        ("de", _("German")),
        ("es", _("Spanish")),
        ("it", _("Italian")),
        ("pt", _("Portuguese")),
    ]

    TIMEZONE_CHOICES = [
        ("UTC", "UTC"),
        ("US/Eastern", "US/Eastern"),
        ("US/Central", "US/Central"),
        ("US/Mountain", "US/Mountain"),
        ("US/Pacific", "US/Pacific"),
        ("Europe/London", "Europe/London"),
        ("Europe/Paris", "Europe/Paris"),
        ("Europe/Zurich", "Europe/Zurich"),
        ("Europe/Berlin", "Europe/Berlin"),
        ("Asia/Tokyo", "Asia/Tokyo"),
        ("Asia/Shanghai", "Asia/Shanghai"),
        ("Australia/Sydney", "Australia/Sydney"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        verbose_name=_("role"),
    )
    bio = models.TextField(_("bio"), blank=True, default="")
    location = models.CharField(_("location"), max_length=255, blank=True, default="")
    website = models.URLField(_("website"), blank=True, default="")
    language = models.CharField(
        _("preferred language"),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en",
    )
    timezone = models.CharField(
        _("timezone"),
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default="UTC",
    )
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    notification_preferences = models.JSONField(
        _("notification preferences"),
        default=dict,
        blank=True,
    )
    is_profile_public = models.BooleanField(
        _("public profile"),
        default=False,
        help_text=_("Whether this profile is publicly visible."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return f"Profile of {self.user.get_display_name()}"

    # Role convenience methods
    def get_role_name(self):
        """Return the name of the assigned role, or 'No role'."""
        if self.role:
            return self.role.name
        return _("No role")

    def get_role_hierarchy_level(self):
        """Return the hierarchy level of the assigned role."""
        if self.role:
            return self.role.hierarchy_level
        return 0

    def has_role(self, role_slug):
        """Check if the user has a specific role by slug."""
        if self.role:
            return self.role.slug == role_slug
        return False

    def has_role_or_higher(self, role_slug):
        """Check if the user has the given role or a higher one."""
        target_level = Role.HIERARCHY_LEVELS.get(role_slug, 0)
        return self.get_role_hierarchy_level() >= target_level

    def has_permission(self, permission_name):
        """Check if the user's role grants a specific permission."""
        if not self.role:
            return False
        return getattr(self.role, permission_name, False)

    def is_admin(self):
        """Check if the user has the admin role."""
        return self.has_role("admin")

    def is_manager_or_above(self):
        """Check if the user is a manager or higher."""
        return self.has_role_or_higher("manager")


# ==========================================
# USER PERMISSION
# ==========================================


class UserPermission(TimeStampedModel):
    """Tracks specific permissions assigned to individual users."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="custom_permissions",
        verbose_name=_("user"),
    )
    permission_name = models.CharField(
        _("permission name"),
        max_length=100,
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="permissions_granted",
        verbose_name=_("granted by"),
    )
    reason = models.TextField(_("reason"), blank=True, default="")
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("user permission")
        verbose_name_plural = _("user permissions")
        unique_together = ["user", "permission_name"]

    def __str__(self):
        return f"{self.user} - {self.permission_name}"


# ==========================================
# TEAM
# ==========================================


class Team(TimeStampedModel):
    """Represents a team within a tenant."""

    name = models.CharField(_("team name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    description = models.TextField(_("description"), blank=True, default="")
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_teams",
        verbose_name=_("team leader"),
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="teams",
        verbose_name=_("members"),
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def member_count(self):
        """Return the number of members in the team."""
        return self.members.count()


# ==========================================
# USER ACTIVITY
# ==========================================


class UserActivity(TimeStampedModel):
    """Logs user activity within the tenant."""

    ACTIVITY_TYPES = [
        ("login", _("Login")),
        ("logout", _("Logout")),
        ("page_view", _("Page View")),
        ("action", _("Action")),
        ("api_call", _("API Call")),
        ("data_export", _("Data Export")),
        ("settings_change", _("Settings Change")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=_("user"),
    )
    activity_type = models.CharField(
        _("activity type"),
        max_length=50,
        choices=ACTIVITY_TYPES,
    )
    description = models.TextField(_("description"), blank=True, default="")
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        blank=True,
        null=True,
    )
    user_agent = models.TextField(_("user agent"), blank=True, default="")
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)

    class Meta:
        verbose_name = _("user activity")
        verbose_name_plural = _("user activities")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.get_activity_type_display()} - {self.created_at}"


# ==========================================
# USER INVITATION
# ==========================================


class UserInvitation(models.Model):
    """Tracks invitations sent to new users."""

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("accepted", _("Accepted")),
        ("expired", _("Expired")),
        ("revoked", _("Revoked")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"))
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations_sent",
        verbose_name=_("invited by"),
    )
    assigned_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
        verbose_name=_("assigned role"),
    )
    code = models.CharField(
        _("invitation code"),
        max_length=64,
        unique=True,
        default=generate_invitation_code,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    message = models.TextField(
        _("personal message"),
        blank=True,
        default="",
    )
    accepted_at = models.DateTimeField(_("accepted at"), blank=True, null=True)
    expires_at = models.DateTimeField(
        _("expires at"),
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("user invitation")
        verbose_name_plural = _("user invitations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation to {self.email} ({self.get_status_display()})"

    @property
    def is_expired(self):
        """Check if the invitation has expired."""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    @property
    def is_valid(self):
        """Check if the invitation is still valid."""
        return self.status == "pending" and not self.is_expired

    def accept(self, user=None):
        """Mark the invitation as accepted."""
        self.status = "accepted"
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at", "updated_at"])

    def revoke(self):
        """Revoke the invitation."""
        self.status = "revoked"
        self.save(update_fields=["status", "updated_at"])


# ==========================================
# SIGNUP CODE & USAGE
# ==========================================


class SignupCode(models.Model):
    """Reusable signup codes for controlled registration."""

    code = models.CharField(
        _("signup code"),
        max_length=50,
        unique=True,
        default=generate_signup_code,
    )
    description = models.TextField(_("description"), blank=True, default="")
    assigned_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signup_codes",
        verbose_name=_("assigned role"),
    )
    max_uses = models.PositiveIntegerField(
        _("maximum uses"),
        default=0,
        help_text=_("0 means unlimited."),
    )
    current_uses = models.PositiveIntegerField(
        _("current uses"),
        default=0,
    )
    is_active = models.BooleanField(_("active"), default=True)
    expires_at = models.DateTimeField(_("expires at"), blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_signup_codes",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("signup code")
        verbose_name_plural = _("signup codes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({self.current_uses}/{self.max_uses or 'unlimited'})"

    @property
    def is_valid(self):
        """Check if the signup code is still valid."""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        return True

    def use(self, user):
        """Record a usage of this signup code."""
        if not self.is_valid:
            return False
        self.current_uses += 1
        self.save(update_fields=["current_uses", "updated_at"])
        SignupCodeUsage.objects.create(signup_code=self, user=user)
        return True


class SignupCodeUsage(models.Model):
    """Tracks individual usage of signup codes."""

    signup_code = models.ForeignKey(
        SignupCode,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name=_("signup code"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="signup_code_usages",
        verbose_name=_("user"),
    )
    used_at = models.DateTimeField(_("used at"), auto_now_add=True)

    class Meta:
        verbose_name = _("signup code usage")
        verbose_name_plural = _("signup code usages")
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.user} used {self.signup_code.code} at {self.used_at}"
