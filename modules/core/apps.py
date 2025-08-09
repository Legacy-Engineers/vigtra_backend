from django.apps import AppConfig
from .config_manager import ConfigManager


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.core"

    def ready(self):
        config_manager = ConfigManager()
        config_manager.initialize_config()
