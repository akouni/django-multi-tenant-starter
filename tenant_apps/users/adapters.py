# tenant_apps/users/adapters.py
# Adapted from PaperPoint users/adapters.py for the multi-tenant starter.

from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter


class TenantAccountAdapter(DefaultAccountAdapter):
    """Custom allauth account adapter for multi-tenant system."""

    def get_login_redirect_url(self, request):
        """Redirect to home page after login."""
        return "/"

    def get_signup_redirect_url(self, request):
        """Redirect to home page after signup."""
        return "/"

    def is_open_for_signup(self, request):
        """
        Control whether signups are open.
        Can be extended to check tenant-level settings.
        """
        return True

    def save_user(self, request, user, form, commit=True):
        """Save the user and perform any additional setup."""
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
        return user


class TenantMFAAdapter(DefaultMFAAdapter):
    """Custom MFA adapter for multi-tenant system."""

    def get_totp_issuer(self):
        """Return the TOTP issuer name for authenticator apps."""
        return "Starter"
