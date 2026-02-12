# tenant_apps/users/views.py

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, ListView

from .forms import UserProfileForm
from .models import CustomUser, UserProfile


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================


class CustomLoginView(LoginView):
    """Custom login view with tenant-specific template."""

    template_name = "tenants/users/login.html"


# ==========================================
# DASHBOARD
# ==========================================


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for authenticated users."""

    template_name = "tenants/users/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


# ==========================================
# PROFILE VIEWS
# ==========================================


@login_required
def profile_view(request):
    """Display the current user's profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
    }
    return render(request, "tenants/users/profile.html", context)


@login_required
def profile_edit(request):
    """Edit the current user's profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }
    return render(request, "tenants/users/profile_edit.html", context)


# ==========================================
# USER LIST (STAFF ONLY)
# ==========================================


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin that requires the user to be staff."""

    def test_func(self):
        return self.request.user.is_staff


class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """List all users. Requires staff access."""

    model = CustomUser
    template_name = "tenants/users/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    ordering = ["-date_joined"]


# ==========================================
# REGISTRATION
# ==========================================


def user_registration(request):
    """Simple user registration view."""
    if request.user.is_authenticated:
        return redirect("users:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        errors = []

        if not username:
            errors.append(_("Username is required."))
        if not email:
            errors.append(_("Email is required."))
        if not password1:
            errors.append(_("Password is required."))
        if password1 != password2:
            errors.append(_("Passwords do not match."))
        if username and CustomUser.objects.filter(username=username).exists():
            errors.append(_("Username is already taken."))
        if email and CustomUser.objects.filter(email=email).exists():
            errors.append(_("Email is already in use."))

        if errors:
            context = {
                "errors": errors,
                "username": username,
                "email": email,
            }
            return render(request, "tenants/users/register.html", context)

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        UserProfile.objects.get_or_create(user=user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, _("Registration successful. Welcome!"))
        return redirect("users:dashboard")

    return render(request, "tenants/users/register.html")
