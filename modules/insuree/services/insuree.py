from typing import Dict
from modules.core.service_signals import register_signal
from modules.insuree.models import Insuree
from modules.core.utils import vigtra_message
import logging

logger = logging.getLogger(__name__)


class InsureeService:
    def __init__(self):
        pass

    @register_signal("insuree_service.create_or_update_insuree")
    def create_or_update(self, data: dict, **kwargs) -> Dict[str, bool | dict | str]:
        uuid = data.get("uuid")

        if uuid:
            return self.update_insuree(data=data)
        else:
            return self.create_insuree(data=data)

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

    @register_signal("insuree_service.update_insuree")
    def update_insuree(self, data: dict, **kwargs) -> Dict[str, bool | str | dict]:
        try:
            uuid = data.get("uuid")
            current_insuree = Insuree.objects.get(uuid=uuid)

            if current_insuree:
                pass
            else:
                return vigtra_message(message="mutation_insuree_not_exist")

        except Exception as exc:
            return vigtra_message(
                message="Unexpected error occured", error_details=[exc], data=data
            )
