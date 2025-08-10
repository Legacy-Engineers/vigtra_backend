from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_eventstream.viewsets import EventsViewSet

router = DefaultRouter()


class NotificationHubEventsViewSet(EventsViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.channels = ["notification-hub"]
        self.messages_types = ["message"]
        self._api_sse = True


router.register(
    "events",
    NotificationHubEventsViewSet,
    basename="events",
)

urlpatterns = [
    path("", include(router.urls)),
]
