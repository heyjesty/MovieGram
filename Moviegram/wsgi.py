"""
WSGI config for Moviegram project.

It exposes the WSGI callable as module-level variables named ``application``
(standard) and ``app`` (used by Vercel's Python runtime).
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Moviegram.settings")

application = get_wsgi_application()

if os.environ.get("VERCEL"):
    from Moviegram.serverless import prepare

    prepare()

app = application
