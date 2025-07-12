from typing import Dict
from modules.core.service_signals import register_signal
from modules.insuree.models import Insuree
from modules.core.utils import vigtra_message
import logging

logger = logging.getLogger(__name__)


class InsureeService:
    def __init__(self):
        pass

    @register_signal("insuree_service.create_insuree")
    def create_insuree(self, data: dict, **kwargs) -> Dict[str, bool | dict | str]:
        try:
            new_insuree = Insuree().objects.create(**data)

            if new_insuree:
                return vigtra_message(
                    success=True,
                    message="Successfully created!",
                    data=new_insuree.__dict__,
                )
        except Exception as exc:
            logger.debug(f"Failed to create insuree data {data}, EXCEPTION: {exc}")
            return vigtra_message(
                message="An unexpected error occured", error_details=[exc], data=data
            )
