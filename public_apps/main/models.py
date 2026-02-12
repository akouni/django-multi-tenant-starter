# public_apps/main/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """Simple contact form message stored in the public schema."""

    name = models.CharField(
        _("Name"),
        max_length=200,
    )
    email = models.EmailField(
        _("Email"),
    )
    subject = models.CharField(
        _("Subject"),
        max_length=300,
    )
    message = models.TextField(
        _("Message"),
    )
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"
