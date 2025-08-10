from django.conf import settings
import os
import yaml
from modules.payment_gateway.apps import DEFAULT_PAYMENT_INTEGRATORS

BASE_DIR = getattr(settings, "BASE_DIR", None)

VIGTRA_CONFIG_FILE = os.path.join(BASE_DIR, "vigtra_core_config.yaml")

DEFAULT_VIGTRA_CONFIG_DATA = {
    "site_config": {
        "logo": "https://www.google.com",
        "name": "Vigtra",
        "description": "Vigtra is a platform for managing claims and health facilities",
        "contact_email": "info@vigtra.com",
        "contact_phone": "+254712345678",
        "contact_address": "123 Main St, Nairobi, Kenya",
        "contact_website": "https://www.vigtra.com",
    },
    "use_qa_accreditation": True,
    "use_mail_manager": True,
    "health_facility": {
        "use_qa_accreditation_filter": True,
    },
    "mail_manager": {
        "email_template": {
            "primary_color": "#000000",
            "secondary_color": "#000000",
            "background_color": "#000000",
            "text_color": "#000000",
            "link_color": "#000000",
            "button_color": "#000000",
            "button_text_color": "#000000",
            "button_background_color": "#000000",
        },
    },
    "fhir_config": {
        "base_url": "https://fhir.example.com",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "token_url": "https://fhir.example.com/token",
        "authorization_url": "https://fhir.example.com/authorize",
        "scopes": ["openid", "profile", "email", "offline_access"],
    },
    "insuree": {
        "chf_config": {
            "prefix": "CHF",
            "auto_generate": True,
            "regex": None,
            "length": 10,
        },
        "extra_filters": [],
        "validation_rules": {
            "identification_regex": None,
        },
        "max_age_of_majority": 18,
    },
    "claim": {
        "code_config": {
            "prefix": "CLM",
            "auto_generate": True,
            "length": 10,
        },
    },
    "authentication": {
        "activate_insuree_user": True,
    },
    "payment_gateway": {
        "activate_payment_gateway": True,
        "activated_payment_gateways": DEFAULT_PAYMENT_INTEGRATORS,
        "external_integrations": [],
    },
}


class ConfigManager:
    @classmethod
    def initialize_config(cls):
        if not os.path.exists(VIGTRA_CONFIG_FILE):
            with open(VIGTRA_CONFIG_FILE, "w") as f:
                yaml.dump(DEFAULT_VIGTRA_CONFIG_DATA, f)

    @classmethod
    def get_config_data(cls):
        config_data = None

        with open(VIGTRA_CONFIG_FILE, "r") as f:
            config_data = yaml.safe_load(f)

        return config_data

    @classmethod
    def get_claim_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("claim", {})

    @classmethod
    def get_health_facility_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("health_facility", {})

    @classmethod
    def get_mail_manager_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("mail_manager", {})

    @classmethod
    def get_site_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("site_config", {})

    @classmethod
    def get_fhir_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("fhir_config", {})

    @classmethod
    def get_insuree_config(cls):
        config_data = cls.get_config_data()
        return config_data.get("insuree", {})
