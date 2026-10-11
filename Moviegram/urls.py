from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("backend.urls")),
    # Old entry points from the previous version of the site.
    path("frontend/homepage/", RedirectView.as_view(pattern_name="home", permanent=True)),
    path("backend/adminlogin/", RedirectView.as_view(pattern_name="dashboard_login", permanent=True)),
    # Uploaded posters. Served by Django because Vercel has no separate media server.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("frontend.urls")),
]
