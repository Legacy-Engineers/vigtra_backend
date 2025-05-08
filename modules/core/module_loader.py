import pathlib
import logging
import importlib
from django.urls import path, include

PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent


logger = logging.getLogger(__name__)

MODULES = [
    {
        "name": "Insuree",
        "module": "modules.insuree",
    },
    {
        "name": "Policy",
        "module": "modules.policy",
    },
    {
        "name": "Claim",
        "module": "modules.claim",
    },
    {
        "name": "Claim AI",
        "module": "modules.claim.claim_ai",
    },
    {
        "name": "Authentication",
        "module": "modules.authentication",
    },
    {
        "name": "Fhir API",
        "module": "modules.fhir_api",
    },
    {
        "name": "Contribution",
        "module": "modules.contribution",
    },
    {
        "name": "Formal Sector",
        "module": "modules.formal_sector",
    },
    {
        "name": "Contract",
        "module": "modules.formal_sector.contract",
    },
    {
        "name": "Location",
        "module": "modules.location",
    },
    {
        "name": "Product",
        "module": "modules.product",
    },
]


def get_module_list():

    modules = []
    for module in MODULES:
        module_name = module["name"]
        module_path = module["module"]
        try:
            # Import the module
            imported_module = __import__(module_path, fromlist=[module_name])
            
            if imported_module:
                modules.append(module_path)
        except ImportError as e:
            logger.warning(f"Error importing {module_name}: {e}")

    return modules

def get_module_urls():
    urls = []
    for module in MODULES:
        module_path = module["module"]
        
        try:
            imported_module = __import__(module_path, fromlist=[module['name']])
            if imported_module:
                module_url = importlib.import_module(f"{module_path}.urls")
                module_app = importlib.import_module(f"{module_path}.apps")
                if hasattr(module_url, "urlpatterns"):
                    if hasattr(module_app, "URL_PREFIX"):
                        url_pattern = path(f"{module_app.URL_PREFIX}", include(module_url.urlpatterns))
                        urls.append(url_pattern)
        except ImportError as e:
            logger.warning(f"Error importing {module['name']}: {e}")
        except AttributeError as e:
            logger.warning(f"No 'urls' module or 'urlpatterns' in {module['name']}: {e}")
    return urls


def get_module_queries():
    queries = []
    for module in MODULES:
        module_path = module["module"]
        try:
            schema_module = importlib.import_module(f"{module_path}.schema")
            if hasattr(schema_module, "Query"):
                queries.append(schema_module.Query)
        except ImportError as e:
            logger.warning(f"Error importing schema for {module['name']}: {e}")
        except AttributeError as e:
            logger.warning(f"No 'Query' in schema for {module['name']}: {e}")
    return queries


def get_module_mutations():
    mutations = []
    for module in MODULES:
        module_path = module["module"]
        try:
            schema_module = importlib.import_module(f"{module_path}.schema")
            if hasattr(schema_module, "Mutation"):
                mutations.append(schema_module.Mutation)
        except ImportError as e:
            logger.warning(f"Error importing schema for {module['name']}: {e}")
        except AttributeError as e:
            logger.warning(f"No 'Mutation' in schema for {module['name']}: {e}")
    return mutations