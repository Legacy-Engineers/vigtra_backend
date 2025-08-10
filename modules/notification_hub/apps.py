from django.apps import AppConfig

URL_PREFIX = "notification-hub"


class NotificationHubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.notification_hub"
