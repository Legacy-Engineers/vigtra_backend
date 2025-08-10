from django.apps import AppConfig

DEFAULT_PAYMENT_INTEGRATORS = [
    {
        "name": "stripe",
        "label": "Stripe",
        "description": "Stripe is a payment processing platform that allows you to accept payments online.",
        "icon": "https://stripe.com/img/v3/home/logo.png",
        "url": "https://stripe.com",
        "is_active": True,
        "is_default": True,
    },
]


class PaymentGatewayConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payment_gateway"
