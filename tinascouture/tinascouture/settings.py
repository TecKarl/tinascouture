"""
Django settings for tinascouture project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY / ENVIRONMENT
# ============================================================

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get(
    "DJANGO_DEBUG"
).lower() in ("1", "true", "yes")


# Controls where uploaded media files are stored.
#
# False -> local media/ directory
# True  -> Supabase Storage

USE_S3_STORAGE = os.environ.get(
    "USE_S3_STORAGE",
    "False",
).lower() in ("1", "true", "yes")


ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# ============================================================
# CORS
# ============================================================
#
# Used for the splash/health-check endpoint.
#
# Only /health/ is subject to CORS.
# ============================================================

CORS_URLS_REGEX = r"^/health/$"

CORS_ALLOWED_ORIGINS = [
    "https://tinascouture.shop",
    "https://www.tinascouture.shop",
    "https://app.tinascouture.shop",
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

    "storages",

    "shop",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "tinascouture.urls"

WSGI_APPLICATION = "tinascouture.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.cart",
            ],
        },
    },
]


# ============================================================
# DATABASE
# ============================================================
#
# Render provides DATABASE_URL.
#
# In production this will be the Supabase PostgreSQL
# connection string.
#
# Locally, if DATABASE_URL is not provided, Django falls
# back to SQLite.
# ============================================================

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# FILE STORAGE
# ============================================================
#
# USE_S3_STORAGE=False
#     -> uploaded files go into local media/
#
# USE_S3_STORAGE=True
#     -> uploaded files go into Supabase Storage
#
# Static files are handled by WhiteNoise in both cases.
# ============================================================

if USE_S3_STORAGE:

    STORAGES = {
        "default": {
            "BACKEND": "shop.storage.SupabaseStorage",

            "OPTIONS": {
                "access_key": os.environ[
                    "SUPABASE_S3_ACCESS_KEY"
                ],

                "secret_key": os.environ[
                    "SUPABASE_S3_SECRET_KEY"
                ],

                "bucket_name": os.environ[
                    "SUPABASE_STORAGE_BUCKET"
                ],

                "endpoint_url": os.environ[
                    "SUPABASE_S3_ENDPOINT"
                ],

                "region_name": os.environ[
                    "SUPABASE_S3_REGION"
                ],

                "addressing_style": "path",

                "signature_version": "s3v4",

                "querystring_auth": False,

                "file_overwrite": False,
            },
        },

        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }

else:

    STORAGES = {
        "default": {
            "BACKEND": (
                "django.core.files.storage."
                "FileSystemStorage"
            ),
        },

        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }


# ============================================================
# MEDIA FILES
# ============================================================
#
# These are used when USE_S3_STORAGE=False.
#
# When USE_S3_STORAGE=True, uploaded files are handled by
# SupabaseStorage instead.
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# AUTHENTICATION
# ============================================================

LOGIN_URL = "shop:login"


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True