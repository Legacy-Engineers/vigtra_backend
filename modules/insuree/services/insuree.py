from typing import Dict
from modules.core.service_signals import register_signal


class InsureeService:
    def __init__(self):
        pass

    @register_signal("insuree_service.create_insuree")
    def create_insuree(self, data: dict) -> Dict[str, bool | dict | str]:
        pass
