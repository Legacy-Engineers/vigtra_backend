from django_eventstream.viewsets import EventsViewSet


class ClaimEventsViewSet(EventsViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.channels = ["claim-events"]
        self.messages_types = ["message"]
        self._api_sse = True
