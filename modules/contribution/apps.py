from django.apps import AppConfig


class ContributionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.openimis_modules.contribution'
    url_prefix = 'contributions'