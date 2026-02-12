# core/middleware.py

from django.contrib import admin
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django_tenants.utils import get_public_schema_name
from django.shortcuts import redirect
from django.utils import translation
from core.tenant_utils import get_current_tenant
import re
import logging

logger = logging.getLogger(__name__)

from .constants import (
    JAZZMIN_SETTINGS_PUBLIC,
    JAZZMIN_UI_TWEAKS_PUBLIC,
    JAZZMIN_SETTINGS_TENANT,
    JAZZMIN_UI_TWEAKS_TENANT,
)


class TenantTypeMiddleware(MiddlewareMixin):
    """Middleware to verify tenant type and prevent wrong admin access."""

    def process_request(self, request):
        if not request.path.startswith("/admin/"):
            return None

        tenant = request.tenant

        if tenant.schema_name == get_public_schema_name():
            if request.urlconf == "core.tenant_urls":
                return HttpResponseForbidden(
                    "Access denied: public schema cannot use tenant admin"
                )
        elif getattr(tenant, "type", None) == "client":
            if request.urlconf == "core.urls":
                return HttpResponseForbidden(
                    "Access denied: client tenant cannot use public admin"
                )

        return None


class JazzminSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'tenant') and request.tenant.schema_name == get_public_schema_name():
            settings.JAZZMIN_SETTINGS = JAZZMIN_SETTINGS_PUBLIC
            settings.JAZZMIN_UI_TWEAKS = JAZZMIN_UI_TWEAKS_PUBLIC
        else:
            settings.JAZZMIN_SETTINGS = JAZZMIN_SETTINGS_TENANT
            settings.JAZZMIN_UI_TWEAKS = JAZZMIN_UI_TWEAKS_TENANT

        response = self.get_response(request)
        return response


class SmartAuthI18nMiddleware:
    """Middleware to handle authentication with i18n redirections."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        response = self.get_response(request)
        return response

    def process_request(self, request):
        path = request.path.rstrip('/')
        accounts_login_pattern = r'^(/[a-z]{2})?/accounts/login/?$'

        if re.match(accounts_login_pattern, path):
            return self.redirect_to_proper_login(request)
        return None

    def redirect_to_proper_login(self, request):
        current_language = self.get_user_language(request)
        login_url = self.build_login_url(current_language)

        query_string = request.GET.urlencode()
        if query_string:
            login_url += f'?{query_string}'

        return redirect(login_url)

    def get_user_language(self, request):
        path_parts = request.path.strip('/').split('/')
        if path_parts and len(path_parts[0]) == 2:
            potential_lang = path_parts[0].lower()
            if potential_lang in [lang[0] for lang in settings.LANGUAGES]:
                return potential_lang

        session_lang = request.session.get('django_language')
        if session_lang and session_lang in [lang[0] for lang in settings.LANGUAGES]:
            return session_lang

        browser_lang = translation.get_language_from_request(request)
        if browser_lang:
            return browser_lang

        return settings.LANGUAGE_CODE

    def build_login_url(self, language_code):
        use_prefix = getattr(settings, 'USE_I18N_PREFIX_DEFAULT_LANGUAGE', True)
        if language_code == settings.LANGUAGE_CODE and not use_prefix:
            return '/users/login/'
        else:
            return f'/{language_code}/users/login/'


class TenantLanguageMiddleware:
    """Middleware to filter available languages by tenant."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.original_languages = settings.LANGUAGES
        self.original_language_code = settings.LANGUAGE_CODE

    def __call__(self, request):
        tenant = get_current_tenant()

        if tenant and hasattr(tenant, 'active_languages') and tenant.active_languages:
            tenant_languages = []
            for lang_code, lang_name in self.original_languages:
                if lang_code in tenant.active_languages:
                    tenant_languages.append((lang_code, lang_name))

            settings.LANGUAGES = tenant_languages

            if hasattr(tenant, 'default_language') and tenant.default_language:
                settings.LANGUAGE_CODE = tenant.default_language

                current_lang = translation.get_language()
                if current_lang and current_lang not in tenant.active_languages:
                    translation.activate(tenant.default_language)
                    request.LANGUAGE_CODE = tenant.default_language
        else:
            settings.LANGUAGES = self.original_languages
            settings.LANGUAGE_CODE = self.original_language_code

        response = self.get_response(request)

        settings.LANGUAGES = self.original_languages
        settings.LANGUAGE_CODE = self.original_language_code

        return response
