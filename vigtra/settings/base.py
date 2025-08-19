from modules.core.module_loader import get_module_list
import os
from pathlib import Path
from .. import BASE_DIR
from ..extra_settings import ExtraSettings


INSTALLED_APPS = [
    # Third party apps
    "daphne",
    "jazzmin",
    # Modules
    "modules.core",
    # Default Django APPS
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_eventstream",
    "guardian",
    "corsheaders",
    "graphene_django",
    "django_filters",
    # "passkeys",  # Temporarily disabled
    "axes",
    "django_lifecycle_checks",
    "simple_history",
    "easyaudit",
    "rest_framework",
    "rest_framework_api_key",
    "graphql_jwt.refresh_token",
    # For development
    "debug_toolbar",
]

INSTALLED_APPS += (
    get_module_list() + THIRD_PARTY_APPS + ExtraSettings.get_extra_third_party_apps()
)
INSTALLED_APPS += ExtraSettings.get_extra_templates()

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "vigtra.middleware.performance.PerformanceMonitoringMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "vigtra.middleware.performance.DatabaseQueryCountMiddleware",
    "easyaudit.middleware.easyaudit.EasyAuditMiddleware",
    # For development
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Third party middleware
THIRD_PARTY_MIDDLEWARE = [
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

MIDDLEWARE += THIRD_PARTY_MIDDLEWARE + ExtraSettings.get_extra_third_party_middleware()

MIDDLEWARE.append("axes.middleware.AxesMiddleware")

ROOT_URLCONF = "vigtra.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates/"] + ExtraSettings.get_extra_templates(),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
            + ExtraSettings.get_extra_context_processors(),
        },
    },
]

WSGI_APPLICATION = "vigtra.wsgi.application"
ASGI_APPLICATION = "vigtra.asgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


DEFAULT_AUTO_FIELD = os.getenv("DEFAULT_AUTO_FIELD", "django.db.models.BigAutoField")


AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    # "passkeys.backend.PasskeyModelBackend",  # Temporarily disabled
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
] + ExtraSettings.get_extra_auth_backends()


# User Auth Model
AUTH_USER_MODEL = "authentication.User"


# settings.py - Media Configuration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Media files (User uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# STATIC_URL and STATIC_ROOT are already defined above

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Allowed file extensions (optional security measure)
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".odt"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]

# Maximum file sizes for different types (in bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# Media storage configuration for production (using AWS S3)
# Uncomment and configure for production use
"""
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_FILE_OVERWRITE = False

# Use S3 for media files in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
"""


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "django_eventstream.renderers.SSEEventRenderer",
        "django_eventstream.renderers.BrowsableAPIEventStreamRenderer",
    ],
}
