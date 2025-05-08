from django.apps import AppConfig


class ClaimConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.claim'
    url_prefix = 'claims'
