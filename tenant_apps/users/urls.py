# tenant_apps/users/urls.py

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.user_registration, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("", views.UserListView.as_view(), name="user_list"),
]
