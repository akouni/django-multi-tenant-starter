# public_apps/main/views.py
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class HomeView(TemplateView):
    template_name = "public/home.html"


class AboutView(TemplateView):
    template_name = "public/about.html"


class ContactView(TemplateView):
    template_name = "public/contact.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if not all([name, email, subject, message_text]):
            messages.error(request, _("Please fill in all fields."))
            return self.get(request, *args, **kwargs)

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text,
        )
        messages.success(
            request,
            _("Thank you for your message! We will get back to you soon."),
        )
        return redirect("main:contact")
