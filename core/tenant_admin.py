# core/tenant_admin.py
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class TenantAdminSite(AdminSite):
    def __init__(self, name="tenant_admin"):
        super().__init__(name)
        self.site_header = _("Administration")
        self.site_title = _("Administration")
        self.index_title = _("Welcome to the Administration Portal")


tenant_admin_site = TenantAdminSite()
