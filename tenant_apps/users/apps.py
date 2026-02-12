# tenant_apps/users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenant_apps.users"
    verbose_name = "Users"
    label = "users"

    def ready(self):
        pass
