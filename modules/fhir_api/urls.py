from django.urls import path, include
from . import fhir_urls

urlpatterns = [
    path("r4/", include(fhir_urls.r4_urls)),
    path("r4b/", include(fhir_urls.r4b_urls)),
    path("r5/", include(fhir_urls.r5_urls)),
    path("r6/", include(fhir_urls.r6_urls)),
]
