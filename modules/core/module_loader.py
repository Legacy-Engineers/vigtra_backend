import pathlib
import logging
import importlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from django.urls import path, include

logger = logging.getLogger(__name__)

PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent


@dataclass
class ModuleConfig:
    """Configuration for a module."""

    name: str
    module: str
    enabled: bool = True


# Module configuration - easier to manage
MODULES = [
    ModuleConfig("Authentication", "modules.authentication"),
    ModuleConfig("Location", "modules.location"),
    ModuleConfig("Insuree", "modules.insuree"),
    ModuleConfig("Insurance Plan", "modules.insurance_plan"),
    ModuleConfig("Insurance Coverage", "modules.insurance_coverage"),
    ModuleConfig("Claim", "modules.claim"),
    ModuleConfig("Claim AI", "modules.claim.claim_ai"),
    ModuleConfig("FHIR API", "modules.fhir_api"),
    ModuleConfig("Contribution", "modules.contribution"),
    ModuleConfig("Contribution Plan", "modules.contribution_plan"),
    ModuleConfig("Formal Sector", "modules.formal_sector"),
    ModuleConfig("Product", "modules.product"),
    ModuleConfig("Preauthorization", "modules.preauthorization"),
    ModuleConfig("Report", "modules.report"),
    ModuleConfig("Payment", "modules.payment"),
    ModuleConfig("Billing", "modules.payment.billing"),
    ModuleConfig("Premium", "modules.payment.premium"),
    ModuleConfig("Contract", "modules.contract"),
    ModuleConfig("Service", "modules.service"),
    ModuleConfig("Medical", "modules.medical"),
    ModuleConfig("Notification Hub", "modules.notification_hub"),
]


class ModuleLoader:
    """Centralized module loading with caching and error handling."""

    def __init__(self):
        self._module_cache = {}
        self._schema_cache = {}

    def _import_module_safely(
        self, module_path: str, module_name: str
    ) -> Optional[Any]:
        """Safely import a module with caching."""
        if module_path in self._module_cache:
            return self._module_cache[module_path]

        try:
            imported_module = importlib.import_module(module_path)
            self._module_cache[module_path] = imported_module
            return imported_module
        except ImportError as e:
            logger.warning(f"Failed to import {module_name} ({module_path}): {e}")
            return None

    def _get_schema_module(self, module_path: str, module_name: str) -> Optional[Any]:
        """Get schema module with caching."""
        schema_path = f"{module_path}.schema"

        if schema_path in self._schema_cache:
            return self._schema_cache[schema_path]

        try:
            schema_module = importlib.import_module(schema_path)
            self._schema_cache[schema_path] = schema_module
            return schema_module
        except ImportError:
            logger.debug(f"No schema module found for {module_name}")
            return None

    def _get_websockets(self) -> List:
        """Get websocket patterns from all modules."""
        websocket_urls = []

        for module_config in MODULES:
            if not module_config.enabled:
                continue

            try:
                websocket_module = importlib.import_module(
                    f"{module_config.module}.websockets"
                )

                if hasattr(websocket_module, "websocket_urlpatterns"):
                    websocket_urls.extend(websocket_module.websocket_urlpatterns)
            except ImportError:
                # Module doesn't have websockets support, skip silently
                logger.debug(f"No websockets module for {module_config.name}")
                continue

        return websocket_urls

    def get_available_modules(self) -> List[str]:
        """Get list of successfully imported module paths."""
        modules = []
        for module_config in MODULES:
            if not module_config.enabled:
                continue

            if self._import_module_safely(module_config.module, module_config.name):
                modules.append(module_config.module)

        return modules

    def get_module_urls(self) -> List[Any]:
        """Get URL patterns from all modules."""
        urls = []

        for module_config in MODULES:
            if not module_config.enabled:
                continue

            # Check if main module exists
            main_module = self._import_module_safely(
                module_config.module, module_config.name
            )
            if not main_module:
                continue

            try:
                # Import URL and app modules
                url_module = importlib.import_module(f"{module_config.module}.urls")
                app_module = importlib.import_module(f"{module_config.module}.apps")

                # Check for required attributes - use getattr for safer access
                urlpatterns = getattr(url_module, "urlpatterns", None)
                if urlpatterns is None:
                    logger.debug(f"No urlpatterns in {module_config.name}")
                    continue

                # Get URL prefix
                if hasattr(app_module, "URL_PREFIX"):
                    url_prefix = getattr(
                        app_module, "URL_PREFIX", module_config.name.lower()
                    )
                else:
                    url_prefix = module_config.name.lower()

                url_pattern = path(f"{url_prefix}/", include(urlpatterns))
                urls.append(url_pattern)

                logger.debug(
                    f"Added URLs for {module_config.name} with prefix '{url_prefix}'"
                )

            except ImportError as e:
                logger.debug(f"No URL module for {module_config.name}: {e}")
            except AttributeError as e:
                logger.debug(f"Missing URL attributes in {module_config.name}: {e}")
            except Exception as e:
                logger.warning(
                    f"Unexpected error processing URLs for {module_config.name}: {e}"
                )

        return urls

    def get_module_queries(self) -> List[Any]:
        """Get GraphQL queries from all modules."""
        queries = []

        for module_config in MODULES:
            if not module_config.enabled:
                continue

            schema_module = self._get_schema_module(
                module_config.module, module_config.name
            )
            if not schema_module:
                continue

            if hasattr(schema_module, "Query"):
                queries.append(schema_module.Query)
                logger.debug(f"Added Query from {module_config.name}")
            else:
                logger.debug(f"No Query class in {module_config.name} schema")

        return queries

    def get_module_mutations(self) -> List[Any]:
        """Get GraphQL mutations from all modules."""
        mutations = []

        for module_config in MODULES:
            if not module_config.enabled:
                continue

            schema_module = self._get_schema_module(
                module_config.module, module_config.name
            )
            if not schema_module:
                continue

            if hasattr(schema_module, "Mutation"):
                mutations.append(schema_module.Mutation)
                logger.debug(f"Added Mutation from {module_config.name}")
            else:
                logger.debug(f"No Mutation class in {module_config.name} schema")

        return mutations

    def get_module_info(self) -> Dict[str, Any]:
        """Get information about all modules."""
        info = {
            "total_modules": len(MODULES),
            "enabled_modules": len([m for m in MODULES if m.enabled]),
            "available_modules": [],
            "unavailable_modules": [],
            "modules_with_schema": [],
            "modules_with_urls": [],
        }

        for module_config in MODULES:
            if not module_config.enabled:
                continue

            module_info = {
                "name": module_config.name,
                "path": module_config.module,
                "imported": False,
                "has_schema": False,
                "has_urls": False,
                "has_query": False,
                "has_mutation": False,
            }

            # Check if module can be imported
            main_module = self._import_module_safely(
                module_config.module, module_config.name
            )
            if main_module:
                module_info["imported"] = True
                info["available_modules"].append(module_info)

                # Check schema
                schema_module = self._get_schema_module(
                    module_config.module, module_config.name
                )
                if schema_module:
                    module_info["has_schema"] = True
                    module_info["has_query"] = hasattr(schema_module, "Query")
                    module_info["has_mutation"] = hasattr(schema_module, "Mutation")
                    info["modules_with_schema"].append(module_config.name)

                # Check URLs
                try:
                    url_module = importlib.import_module(f"{module_config.module}.urls")
                    if hasattr(url_module, "urlpatterns"):
                        module_info["has_urls"] = True
                        info["modules_with_urls"].append(module_config.name)
                except ImportError:
                    pass

            else:
                info["unavailable_modules"].append(module_info)

        return info


# Create singleton instance
_loader = ModuleLoader()


# Simple functions for backward compatibility
def get_module_list() -> List[str]:
    """Get list of available module paths."""
    return _loader.get_available_modules()


def get_module_urls() -> List[Any]:
    """Get URL patterns from all modules."""
    return _loader.get_module_urls()


def get_module_queries() -> List[Any]:
    """Get GraphQL queries from all modules."""
    return _loader.get_module_queries()


def get_module_mutations() -> List[Any]:
    """Get GraphQL mutations from all modules."""
    return _loader.get_module_mutations()


def get_module_info() -> Dict[str, Any]:
    """Get detailed information about all modules."""
    return _loader.get_module_info()


# Helper function to disable/enable modules at runtime
def set_module_enabled(module_name: str, enabled: bool) -> bool:
    """Enable or disable a module by name."""
    for module_config in MODULES:
        if module_config.name == module_name:
            module_config.enabled = enabled
            # Clear cache to force re-evaluation
            _loader._module_cache.clear()
            _loader._schema_cache.clear()
            return True
    return False
