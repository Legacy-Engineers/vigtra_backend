from django.urls import path, include
from rest_framework.routers import DefaultRouter
from modules.notification_hub import views

router = DefaultRouter()


router.register(
    "claim-events",
    views.ClaimEventsViewSet,
    basename="claim-events",
)

urlpatterns = [
    path("", include(router.urls)),
]
