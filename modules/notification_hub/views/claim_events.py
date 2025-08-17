from django_eventstream.viewsets import EventsViewSet
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status


class ClaimEventsViewSet(EventsViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.channels = cache.get("claim_events_channels", [])
        self.messages_types = ["message"]
        self._api_sse = True

    def list(self, request):
        if len(self.channels) > 0 and request.query_params.get("channels"):
            return Response(
                {
                    "error": "Conflicting channel specifications in ViewSet configuration and query parameters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.query_params.get("messages_types"):
            if len(self.messages_types) > 0:
                return Response(
                    {
                        "error": "Conflicting messages types specifications in ViewSet configuration and query parameters."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.messages_types = request.query_params.get("messages_types", "").split(
                ","
            )

        if len(self.channels) == 0:
            self.channels = (
                request.query_params.get("channels", "").split(",")
                if request.query_params.get("channels")
                else []
            )

        return self._stream_or_respond(self.channels, request)
