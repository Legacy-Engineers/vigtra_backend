from typing import Dict
from modules.core.service_signals import register_signal
from modules.insuree.models import Insuree, Gender, IdentificationType
from modules.core.utils import vigtra_message
from modules.insuree.utils import generate_insuree_chf_id
from modules.authentication.models import User
from modules.location.models import HealthFacility
import logging
from datetime import date
import re
import traceback

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
    def create_insuree(
        self, data: dict, user: User, **kwargs
    ) -> Dict[str, bool | dict | str]:
        try:
            insuree_validation = self.validate_and_parse_create_insuree_data(data=data)
            if not insuree_validation.get("success"):
                return insuree_validation

            validated_data = insuree_validation.get("data")
            validated_data["audit_user"] = user
            other_health_facilities = validated_data.pop("other_health_facilities")
            new_insuree: Insuree = Insuree.objects.create(**validated_data)

            if other_health_facilities:
                for health_facility in other_health_facilities:
                    new_insuree.other_health_facilities.set(health_facility)

            if new_insuree:
                return vigtra_message(
                    success=True,
                    message="Successfully created!",
                    data=new_insuree,
                )
        except Exception as exc:
            tb_str = traceback.format_exc()
            logger.debug(
                f"Failed to create insuree data {data}, EXCEPTION: {exc}\nTRACEBACK:\n{tb_str}"
            )
            return vigtra_message(
                message="An unexpected error occured",
                error_details=[str(exc), tb_str],
                data=data,
            )

    @register_signal("insuree_service.validate_and_parse_create_insuree_data")
    def validate_and_parse_create_insuree_data(
        self, data: dict, **kwargs
    ) -> Dict[str, bool | dict | str]:
        try:
            required_fields = [
                "last_name",
                "other_names",
                "dob",
                "gender_code",
                "location_id",
            ]
            for field in required_fields:
                if not data.get(field):
                    return vigtra_message(
                        message=f"Missing required field: {field}",
                        data=data,
                        error_details=[f"Missing required field: {field}"],
                    )

            auto_generate_chf_id = data.pop("auto_generate_chf_id", True)
            gender_code = data.pop("gender_code", None)
            health_facility_code = data.pop("health_facility_code", None)
            secondary_health_facility_code = data.pop(
                "secondary_health_facility_code", None
            )
            other_health_facility_codes = data.pop("other_health_facility_codes", [])
            status = data.get("status", None)

            if status:
                data["status_date"] = date.today()

            if auto_generate_chf_id:
                data["chf_id"] = generate_insuree_chf_id()

            if data.get("chf_id"):
                data["chf_id"] = data["chf_id"].upper()
                if self._check_if_chf_id_exists(data["chf_id"]):
                    data["chf_id"] = generate_insuree_chf_id()

            gender = self._validate_gender_code(gender_code)
            if not gender:
                return vigtra_message(
                    message="Invalid gender code",
                    data=data,
                    error_details=[f"Invalid gender code {gender_code}"],
                )
            else:
                data["gender"] = gender

            if health_facility_code:
                health_facility = self._validate_health_facility_code(
                    health_facility_code
                )
                if not health_facility:
                    return vigtra_message(
                        message="Invalid health facility code",
                        data=data,
                        error_details=[
                            f"Invalid health facility code {health_facility_code}"
                        ],
                    )
                else:
                    data["health_facility"] = health_facility

            if secondary_health_facility_code:
                secondary_health_facility = self._validate_health_facility_code(
                    secondary_health_facility_code
                )
                if not secondary_health_facility:
                    return vigtra_message(
                        message="Invalid secondary health facility code",
                        data=data,
                        error_details=[
                            f"Invalid secondary health facility code {secondary_health_facility_code}"
                        ],
                    )
                else:
                    data["secondary_health_facility"] = secondary_health_facility

            other_health_facilities = []
            if other_health_facility_codes:
                for code in other_health_facility_codes:
                    other_health_facility = self._validate_health_facility_code(code)
                    if other_health_facility:
                        other_health_facilities.append(other_health_facility)
                    else:
                        return vigtra_message(
                            message=f"Invalid other health facility code {code}",
                            data=data,
                            error_details=[
                                f"Invalid other health facility code {code}"
                            ],
                        )

            data["other_health_facilities"] = other_health_facilities

            return vigtra_message(
                success=True,
                message="Successfully validated and parsed data",
                data=data,
            )
        except Exception as exc:
            return vigtra_message(
                message="An unexpected error occured", error_details=[exc], data=data
            )

    def _validate_gender_code(self, gender_code: str) -> bool:
        try:
            gender_obj = Gender.objects.get(code=gender_code)
            if gender_obj:
                return gender_obj
            else:
                return None
        except Gender.DoesNotExist:
            logger.debug(f"Gender code {gender_code} does not exist")
            return None
        except Exception as exc:
            logger.debug(
                f"Failed to validate gender code {gender_code}, EXCEPTION: {exc}"
            )
            return None

    def _validate_health_facility_code(self, health_facility_code: str) -> bool:
        hf_obj = HealthFacility.objects.filter(
            code=health_facility_code, validity_from__isnull=True
        )

        if hf_obj.exists():
            return hf_obj.first()
        else:
            return None

    def _validate_identification_type(
        self, identification_type_code: str, identification_number: str
    ) -> bool:
        prepared_identification_number = None

        if identification_number:
            if identification_type_code:
                try:
                    identification_type_obj = IdentificationType.objects.get(
                        code=identification_type_code
                    )
                    regex_value = f"{identification_type_obj.prefix}{identification_number}{identification_type_obj.suffix}"
                    is_valid_regex = re.match(
                        identification_type_obj.regex, regex_value
                    )
                    if is_valid_regex:
                        prepared_identification_number = regex_value
                    else:
                        return vigtra_message(
                            message="Invalid identification number",
                            data={
                                "identification_type_code": identification_type_code,
                                "identification_number": identification_number,
                            },
                        )
                except Exception as exc:
                    return vigtra_message(
                        message="Invalid identification type code",
                        data={
                            "identification_type_code": identification_type_code,
                            "identification_number": identification_number,
                        },
                        error_details=[exc],
                    )
            else:
                return vigtra_message(
                    message="Invalid identification type code",
                    data={
                        "identification_type_code": identification_type_code,
                        "identification_number": identification_number,
                    },
                )

        return prepared_identification_number

    def _check_if_chf_id_exists(self, chf_id: str) -> bool:
        return Insuree.objects.filter(chf_id=chf_id).exists()

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
