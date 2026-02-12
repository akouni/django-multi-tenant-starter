# core/tenant_urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect

from core.tenant_admin import tenant_admin_site

urlpatterns = [
    path("i18n/setlang/", csrf_exempt(set_language), name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("tinymce/", include("tinymce.urls")),
    path("", lambda request: redirect("users:dashboard"), name="home_redirect"),
]

urlpatterns += i18n_patterns(
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", tenant_admin_site.urls),
    path("accounts/", include("allauth.urls")),
    path("users/", include("tenant_apps.users.urls", namespace="users")),
    path("geomap/", include("tenant_apps.geomap.urls", namespace="geomap")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
