from django.apps import AppConfig


class FhirApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.fhir_api'
    url_prefix = 'fhir-api'
