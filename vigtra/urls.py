from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"api/", include("modules.core.urls")),
    path(r"passkeys/", include("passkeys.urls")),
]
