from django.apps import AppConfig

URL_PREFIX = 'claim-ai'

class ClaimAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.claim.claim_ai'
