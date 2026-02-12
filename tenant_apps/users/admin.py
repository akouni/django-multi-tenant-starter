# tenant_apps/users/admin.py
# Adapted from PaperPoint users/admin.py for the multi-tenant starter.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from core.admin_utils import register_everywhere

from .models import (
    CustomUser,
    UserProfile,
    UserInvitation,
    Role,
    SignupCode,
    SignupCodeUsage,
    UserPermission,
    Team,
    UserActivity,
)


# ==========================================
# INLINES
# ==========================================


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"
    extra = 0


# ==========================================
# CUSTOM USER ADMIN
# ==========================================


@register_everywhere(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "department",
        "job_title",
        "is_email_verified",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_email_verified",
        "department",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "department",
        "job_title",
    )
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "avatar",
                )
            },
        ),
        (
            _("Organization"),
            {
                "fields": (
                    "department",
                    "job_title",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# ==========================================
# USER PROFILE ADMIN
# ==========================================


@register_everywhere(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "location",
        "language",
        "timezone",
        "is_profile_public",
        "created_at",
    )
    list_filter = (
        "role",
        "language",
        "is_profile_public",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "location",
        "bio",
    )
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


# ==========================================
# ROLE ADMIN
# ==========================================


@register_everywhere(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "hierarchy_level",
        "is_default",
        "can_manage_users",
        "can_manage_content",
        "can_view_reports",
    )
    list_filter = (
        "is_default",
        "can_manage_users",
        "can_manage_roles",
        "can_manage_settings",
        "can_manage_content",
    )
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "hierarchy_level",
                    "is_default",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "can_manage_users",
                    "can_manage_roles",
                    "can_manage_settings",
                    "can_manage_content",
                    "can_view_reports",
                    "can_export_data",
                    "can_invite_users",
                    "can_delete_content",
                ),
            },
        ),
        (
            _("Dates"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


# ==========================================
# USER INVITATION ADMIN
# ==========================================


@register_everywhere(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "invited_by",
        "assigned_role",
        "status",
        "created_at",
        "expires_at",
    )
    list_filter = ("status", "assigned_role")
    search_fields = ("email", "invited_by__username", "invited_by__email")
    readonly_fields = ("id", "code", "created_at", "updated_at", "accepted_at")
    raw_id_fields = ("invited_by",)


# ==========================================
# SIGNUP CODE ADMIN
# ==========================================


@register_everywhere(SignupCode)
class SignupCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "description",
        "assigned_role",
        "max_uses",
        "current_uses",
        "is_active",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_active", "assigned_role")
    search_fields = ("code", "description")
    readonly_fields = ("current_uses", "created_at", "updated_at")
    raw_id_fields = ("created_by",)


# ==========================================
# SIGNUP CODE USAGE ADMIN
# ==========================================


@register_everywhere(SignupCodeUsage)
class SignupCodeUsageAdmin(admin.ModelAdmin):
    list_display = (
        "signup_code",
        "user",
        "used_at",
    )
    list_filter = ("used_at",)
    search_fields = (
        "signup_code__code",
        "user__username",
        "user__email",
    )
    raw_id_fields = ("signup_code", "user")
    readonly_fields = ("used_at",)


# ==========================================
# USER PERMISSION ADMIN
# ==========================================


@register_everywhere(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "permission_name",
        "granted_by",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "permission_name")
    search_fields = (
        "user__username",
        "user__email",
        "permission_name",
    )
    raw_id_fields = ("user", "granted_by")
    readonly_fields = ("created_at", "updated_at")


# ==========================================
# TEAM ADMIN
# ==========================================


@register_everywhere(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "leader",
        "member_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("leader",)
    filter_horizontal = ("members",)
    readonly_fields = ("created_at", "updated_at")


# ==========================================
# USER ACTIVITY ADMIN
# ==========================================


@register_everywhere(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "activity_type",
        "ip_address",
        "created_at",
    )
    list_filter = ("activity_type", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "description",
        "ip_address",
    )
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
