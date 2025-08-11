from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")


urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"api/", include("modules.core.urls")),
    # path(r"passkeys/", include("passkeys.urls")),  # Temporarily disabled
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()
