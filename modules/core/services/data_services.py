from typing import List
from modules.authentication.models import User
from ..utils import vigtra_message
from ..module_loader import OPENIMIS_MODULES, VIGTRA_MODULES
import importlib
import logging

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, user: User):
        self.user = user

    @classmethod
    def load_default_data_from_modules(cls)-> List[vigtra_message]:
        modules = OPENIMIS_MODULES + VIGTRA_MODULES

        results = []

        for module in modules:
            validate = cls._validate_module(module)

            if not validate:
                logger.error(f"Module {module['name']} is not valid")

                result_data = {
                    "success": False,
                    "message": f"Module {module['name']} is not valid",
                    "data": None
                }
                results.append(result_data)
                continue
            else:
                pass

    @classmethod
    def _validate_module(cls, module: dict)-> bool:
        module_imp = importlib.import_module(module["module"])

        if not hasattr(module_imp, "load_default_data"):
            return False
        
        if not callable(getattr(module_imp, "load_default_data")):
            return False
        return True