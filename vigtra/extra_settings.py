import os
import yaml
import logging
from vigtra import EXTRA_SETTINGS_CONFIG_FILE
import importlib

logger = logging.getLogger(__name__)

DEFAULT_EXTRA_SETTINGS = {
    "modules": [
        {
            "name": "Sample Name",
            "module": "sample_app",
            "url": "prefix",
            "schema": "sample_app.schema.schema",
            "router": "sample_app.router.router",
        },
    ],
    "templates": [
        "vigtra.templates",
    ],
    "third_party_apps": [
        "sample_app",
    ],
    "third_party_middleware": [
        "sample_app.middleware.SampleMiddleware",
    ],
    "third_party_urls": [
        "sample_app.urls",
    ],
    "context_processors": [
        "sample_app.context_processors.sample_context_processor",
    ],
    "auth_backends": [
        "sample_app.auth.SampleAuthBackend",
    ],
    "auth_permissions": [
        "sample_app.permissions.SamplePermission",
    ],
    "auth_signals": [
        "sample_app.signals.SampleSignal",
    ],
    "extra_cache_settings": [
        {
            "name": "sample_cache",
            "backend": "django.core.cache.backends.locmem.LocMemCache",
            "options": {
                "max_connections": 50,
            },
            "key_prefix": "sample_cache",
            "timeout": 60,
        },
    ],
}


class ExtraSettings:
    @classmethod
    def check_extra_settings_file(cls):
        if not os.path.exists(EXTRA_SETTINGS_CONFIG_FILE):
            logger.warning(
                f"Extra settings file not found: {EXTRA_SETTINGS_CONFIG_FILE}, generating default settings"
            )
            cls.generate_extra_settings()

    @classmethod
    def get_extra_cache_settings(cls):
        data = cls.get_extra_settings_data()
        extra_cache_settings = data.get("extra_cache_settings", [])

        caches = []

        for cache in extra_cache_settings:
            cache_name = cache.get("name", None)
            cache_backend = cache.get("backend", None)
            cache_options = cache.get("options", {})
            cache_key_prefix = cache.get("key_prefix", None)
            cache_timeout = cache.get("timeout", None)

            prepared_cache = {
                f"{cache_name}": {
                    "BACKEND": cache_backend,
                    "OPTIONS": cache_options,
                    "KEY_PREFIX": cache_key_prefix,
                    "TIMEOUT": cache_timeout,
                },
            }
            caches.append(prepared_cache)

        return caches

    @classmethod
    def get_extra_modules(cls):
        data = cls.get_extra_settings_data()
        modules = data.get("modules", [])

        validated_modules = []
        invalid_modules = []
        app_urls = []
        app_schema_queries = []
        app_schema_mutations = []
        app_routers = []

        for module in modules:
            try:
                importlib.import_module(module["module"])
                app_urls.append(module["url"])
                app_schema_queries.append(getattr(module["schema"], "Query"))
                app_schema_mutations.append(getattr(module["schema"], "Mutation"))
                app_routers.append(module["router"])
                validated_modules.append(module)
            except ImportError:
                invalid_modules.append(module["module"])
            except Exception as e:
                logger.error(f"Error importing module: {module['module']}")
                raise e

        return {
            "validated_modules": validated_modules,
            "invalid_modules": invalid_modules,
            "app_urls": app_urls,
            "app_schema_queries": app_schema_queries,
            "app_schema_mutations": app_schema_mutations,
            "app_routers": app_routers,
        }

    @classmethod
    def vigtra_modules(cls):
        extra_modules = cls.get_extra_modules()
        return extra_modules["validated_modules"]

    @classmethod
    def vigtra_urls(cls):
        extra_modules = cls.get_extra_modules()
        return extra_modules["app_urls"]

    @classmethod
    def vigtra_schemas(cls):
        extra_modules = cls.get_extra_modules()
        return extra_modules["app_schemas"]

    @classmethod
    def vigtra_routers(cls):
        extra_modules = cls.get_extra_modules()
        return extra_modules["app_routers"]

    @classmethod
    def validate_modules(cls, modules: list[str]):
        validated_modules = []
        invalid_modules = []
        for module in modules:
            try:
                importlib.import_module(module)
                validated_modules.append(module)
            except ImportError:
                invalid_modules.append(module)
            except Exception as e:
                logger.error(f"Error importing module: {module}")
                raise e

        return validated_modules, invalid_modules

    @classmethod
    def get_extra_third_party_urls(cls):
        data = cls.get_extra_settings_data()
        third_party_urls = data.get("third_party_urls", [])
        validated_third_party_urls, invalid_third_party_urls = cls.validate_modules(
            third_party_urls
        )

        if invalid_third_party_urls:
            logger.warning(f"Invalid third party urls: {invalid_third_party_urls}")

        return validated_third_party_urls

    @classmethod
    def get_extra_context_processors(cls):
        data = cls.get_extra_settings_data()
        context_processors = data.get("context_processors", [])
        validated_context_processors, invalid_context_processors = cls.validate_modules(
            context_processors
        )

        if invalid_context_processors:
            logger.warning(f"Invalid context processors: {invalid_context_processors}")

        return validated_context_processors

    @classmethod
    def get_extra_auth_backends(cls):
        data = cls.get_extra_settings_data()
        auth_backends = data.get("auth_backends", [])
        validated_auth_backends, invalid_auth_backends = cls.validate_modules(
            auth_backends
        )

        if invalid_auth_backends:
            logger.warning(f"Invalid auth backends: {invalid_auth_backends}")

        return validated_auth_backends

    @classmethod
    def get_extra_auth_permissions(cls):
        data = cls.get_extra_settings_data()
        auth_permissions = data.get("auth_permissions", [])
        validated_auth_permissions, invalid_auth_permissions = cls.validate_modules(
            auth_permissions
        )

        if invalid_auth_permissions:
            logger.warning(f"Invalid auth permissions: {invalid_auth_permissions}")

        return validated_auth_permissions

    @classmethod
    def get_extra_third_party_middleware(cls):
        data = cls.get_extra_settings_data()
        third_party_middleware = data.get("third_party_middleware", [])
        validated_third_party_middleware, invalid_third_party_middleware = (
            cls.validate_modules(third_party_middleware)
        )

        if invalid_third_party_middleware:
            logger.warning(
                f"Invalid third party middleware: {invalid_third_party_middleware}"
            )

        return validated_third_party_middleware

    @classmethod
    def get_extra_auth_signals(cls):
        data = cls.get_extra_settings_data()
        auth_signals = data.get("auth_signals", [])
        validated_auth_signals, invalid_auth_signals = cls.validate_modules(
            auth_signals
        )

        if invalid_auth_signals:
            logger.warning(f"Invalid auth signals: {invalid_auth_signals}")

        return validated_auth_signals

    @classmethod
    def get_extra_third_party_apps(cls):
        data = cls.get_extra_settings_data()
        third_party_apps = data.get("third_party_apps", [])
        validated_third_party_apps, invalid_third_party_apps = cls.validate_modules(
            third_party_apps
        )

        if invalid_third_party_apps:
            logger.warning(f"Invalid third party apps: {invalid_third_party_apps}")

        return validated_third_party_apps

    @classmethod
    def get_extra_templates(cls):
        data = cls.get_extra_settings_data()
        templates = data.get("templates", [])

        validated_templates, invalid_templates = cls.validate_modules(templates)

        if invalid_templates:
            logger.warning(f"Invalid templates: {invalid_templates}")

        return validated_templates

    @classmethod
    def get_extra_settings_data(cls):
        try:
            cls.check_extra_settings_file()
            with open(EXTRA_SETTINGS_CONFIG_FILE, "r") as f:
                return yaml.safe_load(f)

        except Exception as e:
            logger.error(f"Error getting extra settings data: {e}")
            raise e

    @classmethod
    def generate_extra_settings(cls):
        logger.info(f"Generating extra settings file: {EXTRA_SETTINGS_CONFIG_FILE}")

        try:
            dump_data = None
            with open(EXTRA_SETTINGS_CONFIG_FILE, "w") as f:
                dump_data = yaml.safe_dump(DEFAULT_EXTRA_SETTINGS, f)

            logger.info(f"Extra settings file generated: {EXTRA_SETTINGS_CONFIG_FILE}")
            logger.info(f"Extra settings file content: {dump_data}")

        except Exception as e:
            logger.error(f"Error generating extra settings file: {e}")
            raise e

        return dump_data
