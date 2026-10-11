"""Cold-start setup for serverless hosting (Vercel).

Vercel's filesystem is read-only except for /tmp, so on each new instance we:
  * copy the bundled posters into the writable media folder,
  * apply migrations (creates and seeds the SQLite database when no DATABASE_URL is set),
  * create a staff account from DJANGO_SUPERUSER_* environment variables, if provided.
"""
import os
import shutil

from django.conf import settings
from django.core.management import call_command


def prepare():
    media_root = settings.MEDIA_ROOT
    if media_root != settings.BUNDLED_MEDIA_ROOT and settings.BUNDLED_MEDIA_ROOT.exists():
        shutil.copytree(settings.BUNDLED_MEDIA_ROOT, media_root, dirs_exist_ok=True)

    call_command("migrate", interactive=False, verbosity=0)
    _ensure_superuser()


def _ensure_superuser():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    if not (username and password):
        return
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
