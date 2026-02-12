# core/public_admin.py
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class PublicAdminSite(AdminSite):
    def __init__(self, name="public_admin"):
        super().__init__(name)
        self.site_header = _("Public Administration")
        self.site_title = _("Administration")
        self.index_title = _("Welcome to the Administration Portal")


public_admin_site = PublicAdminSite()
