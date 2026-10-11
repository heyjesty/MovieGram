"""
Django settings for Moviegram project.

Configuration is read from environment variables so the same code runs locally
and on Vercel. See README.md for the full list.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel sets VERCEL=1. Its filesystem is read-only apart from /tmp.
ON_VERCEL = bool(os.environ.get("VERCEL"))
WRITABLE_DIR = Path("/tmp") if ON_VERCEL else BASE_DIR

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-local-development-key-change-me")

DEBUG = os.environ.get("DJANGO_DEBUG", "0" if ON_VERCEL else "1") == "1"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".vercel.app"]
ALLOWED_HOSTS += [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
CSRF_TRUSTED_ORIGINS += [o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "backend",
    "frontend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Moviegram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "frontend.context_processors.store",
            ],
        },
    },
]

WSGI_APPLICATION = "Moviegram.wsgi.application"

# Use DATABASE_URL (e.g. Postgres from Neon / Vercel Marketplace) when provided.
# Without it, SQLite is used; on Vercel that file lives in /tmp and is rebuilt on cold starts.
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=60, conn_health_checks=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": WRITABLE_DIR / ("moviegram.sqlite3" if ON_VERCEL else "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Signed-cookie sessions survive across serverless instances.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_USE_FINDERS = True

MEDIA_URL = "/media/"
BUNDLED_MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT = WRITABLE_DIR / "media" if ON_VERCEL else BUNDLED_MEDIA_ROOT

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
