# core/settings.py

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-me-in-production-xxxxxxxxxxxxxxxxxxxxxxxxx'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".localhost",
]

# Add custom domain from env
_domain = os.environ.get('DOMAIN_NAME', '')
if _domain and _domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_domain)
    ALLOWED_HOSTS.append(f'.{_domain}')


# ==========================================
# MULTI-TENANT CONFIGURATION
# ==========================================

TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain"

HAS_MULTI_TYPE_TENANTS = True
MULTI_TYPE_DATABASE_FIELD = "type"

TENANT_TYPES = {
    "public": {
        "APPS": [
            "django_tenants",
            "jazzmin",
            "public_apps.customers",
            "modeltranslation",
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "tenant_apps.users",
            "django.contrib.admin",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django.contrib.sites",
            "django.contrib.flatpages",
            "django.contrib.humanize",
            "django.contrib.admindocs",
            "django.contrib.gis",
            "django.contrib.postgres",
            # django-allauth
            "allauth",
            "allauth.account",
            "allauth.mfa",
            # Third-party
            "rest_framework",
            "rest_framework.authtoken",
            "django_filters",
            "widget_tweaks",
            "django_json_widget",
            "django_countries",
            "phonenumber_field",
            "corsheaders",
            "import_export",
            "drf_spectacular",
            "storages",
            "colorfield",
            "csp",
            "tinymce",
            # Local apps
            "public_apps.main",
        ],
        "URLCONF": "core.public_urls",
    },
    "client": {
        "APPS": [
            "modeltranslation",
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "tenant_apps.users",
            "django.contrib.admin",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django.contrib.sites",
            "django.contrib.flatpages",
            "django.contrib.humanize",
            "django.contrib.admindocs",
            "django.contrib.gis",
            "django.contrib.postgres",
            # django-allauth
            "allauth",
            "allauth.account",
            "allauth.mfa",
            # Third-party
            "rest_framework",
            "rest_framework.authtoken",
            "django_filters",
            "widget_tweaks",
            "django_json_widget",
            "django_countries",
            "phonenumber_field",
            "import_export",
            "drf_spectacular",
            "rest_framework_gis",
            "storages",
            "colorfield",
            "csp",
            "tinymce",
            # Local apps
            "tenant_apps.geomap",
        ],
        "URLCONF": "core.tenant_urls",
    },
}

# Build INSTALLED_APPS from tenant types
INSTALLED_APPS = []
for schema in TENANT_TYPES:
    INSTALLED_APPS += [
        app for app in TENANT_TYPES[schema]["APPS"] if app not in INSTALLED_APPS
    ]

PUBLIC_SCHEMA_NAME = 'public'
PG_EXTRA_SEARCH_PATHS = ["extensions"]
ORIGINAL_BACKEND = "django.contrib.gis.db.backends.postgis"

PUBLIC_SCHEMA_URLCONF = "core.public_urls"
ROOT_URLCONF = "core.tenant_urls"

SITE_ID = 1
SITE_NAME = "Multi-Tenant Starter"


# ==========================================
# DRF SPECTACULAR
# ==========================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Multi-Tenant Starter API',
    'DESCRIPTION': 'API documentation for Multi-Tenant Starter',
    'VERSION': '1.0.0',
}

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "core.middleware.JazzminSettingsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "core.middleware.SmartAuthI18nMiddleware",
    "core.middleware.TenantLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.TenantTypeMiddleware",
    "csp.middleware.CSPMiddleware",
]

APPEND_SLASH = True

# ==========================================
# CONTENT SECURITY POLICY (CSP)
# ==========================================

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://unpkg.com",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ],
        "style-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com",
            "'unsafe-inline'",
        ],
        "style-src-elem": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com",
            "'unsafe-inline'",
        ],
        "font-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.gstatic.com",
            "data:",
        ],
        "frame-src": ["'self'"],
        "worker-src": ["'self'", "blob:"],
        "media-src": ["'self'", "blob:", "data:"],
        "connect-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com",
            "https://fonts.gstatic.com",
            "https://*.openstreetmap.org",
            "https://*.tile.openstreetmap.org",
        ],
        "img-src": [
            "'self'",
            "https:",
            "data:",
            "blob:",
            "https://*.openstreetmap.org",
            "https://*.tile.openstreetmap.org",
        ],
    }
}

# Admin titles per tenant type
ADMIN_TITLES = {
    "public": {
        "site_header": _("Main Site Administration"),
        "site_title": _("Starter Administration"),
        "index_title": _("Administration Dashboard"),
    },
    "client": {
        "site_header": _("Client Tenant Administration"),
        "site_title": _("Client Administration Area"),
        "index_title": _("Client Dashboard"),
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.tenant_context",
                "core.context_processors.user_context",
                "core.context_processors.settings_context",
                "public_apps.main.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.environ.get("POSTGRES_DB", "starter_db"),
        "USER": os.environ.get("POSTGRES_USER", "starter_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "change_me"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]

# ==========================================
# AUTH
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.CustomUser'

from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy("users:login")
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/users/login/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "fr")
MODELTRANSLATION_AUTO_POPULATE = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('en',),
    'fr': ('en',),
}

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_PATH = "/"
LANGUAGE_COOKIE_SECURE = not DEBUG
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = "Lax"

# ==========================================
# STATIC & MEDIA
# ==========================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# S3/MINIO STORAGE (optional)
# ==========================================

USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'starter-media')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', None)
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', None)
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_QUERYSTRING_AUTH = os.environ.get('AWS_QUERYSTRING_AUTH', 'True').lower() == 'true'
    AWS_QUERYSTRING_EXPIRE = 3600
    AWS_S3_ADDRESSING_STYLE = os.environ.get('AWS_S3_ADDRESSING_STYLE', 'auto')

    STORAGES = {
        "default": {"BACKEND": "core.storage.TenantMediaStorage"},
        "private": {"BACKEND": "core.storage.TenantPrivateStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    elif AWS_S3_ENDPOINT_URL:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/"

# ==========================================
# PHONENUMBER
# ==========================================

PHONENUMBER_DEFAULT_REGION = "CH"
PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# REST FRAMEWORK
# ==========================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

# ==========================================
# EMAIL
# ==========================================

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@localhost')

# ==========================================
# CACHE (Redis)
# ==========================================

_redis_host = os.environ.get('REDIS_HOST', 'redis')
_redis_port = os.environ.get('REDIS_PORT', '6379')

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{_redis_host}:{_redis_port}/1",
        "KEY_PREFIX": "starter",
        "TIMEOUT": 300,
    },
    'tenant': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{_redis_host}:{_redis_port}/2',
        'KEY_PREFIX': 'tenant',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 86400

# ==========================================
# LOGGING
# ==========================================

os.makedirs(BASE_DIR / "logs", exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "logs" / "app.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "clients": {"handlers": ["console", "file"], "level": "INFO", "propagate": True},
        "core.routers": {"handlers": ["console", "file"], "level": "INFO", "propagate": True},
    },
}

# ==========================================
# JAZZMIN
# ==========================================

from .constants import JAZZMIN_SETTINGS_TENANT, JAZZMIN_UI_TWEAKS_TENANT

JAZZMIN_SETTINGS = JAZZMIN_SETTINGS_TENANT
JAZZMIN_UI_TWEAKS = JAZZMIN_UI_TWEAKS_TENANT

# ==========================================
# TINYMCE
# ==========================================

TINYMCE_DEFAULT_CONFIG = {
    "height": 300,
    "width": "100%",
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 10,
    "selector": "textarea",
    "theme": "silver",
    "plugins": "link image media preview table code lists fullscreen",
    "menubar": True,
    "statusbar": True,
}

# ==========================================
# DJANGO-ALLAUTH
# ==========================================

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 3

ACCOUNT_ADAPTER = "tenant_apps.users.adapters.TenantAccountAdapter"

ACCOUNT_LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/users/login/"

ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_TEMPLATE_EXTENSION = "html"

# ==========================================
# MFA
# ==========================================

MFA_ADAPTER = "tenant_apps.users.adapters.TenantMFAAdapter"
MFA_SUPPORTED_TYPES = ["totp"]
MFA_PASSKEY_LOGIN_ENABLED = False
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = False
MFA_TOTP_PERIOD = 30
MFA_TOTP_DIGITS = 6
MFA_TOTP_ISSUER = "Multi-Tenant Starter"
MFA_RECOVERY_CODE_COUNT = 10
