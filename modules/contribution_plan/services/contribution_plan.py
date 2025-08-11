from typing import Dict
from modules.contribution_plan.models.contribution_plan import (
    ContributionPlan,
    ContributionPlanType,
    ContributionCalculationType,
    ContributionFrequency,
    ContributionPlanStatus,
)
from modules.core.service_signals import register_signal
from modules.core.utils import vigtra_message
from modules.authentication.models.user import User
from ..utils import contribution_plan_config, generate_contribution_plan_code
import logging
import traceback

logger = logging.getLogger(__name__)


class ContributionPlanService:
    @register_signal("contribution_plan.create_contribution_plan")
    def create_contribution_plan(
        self, data: dict, user: User, **kwargs
    ) -> Dict[str, str | dict | list[str] | bool]:
        try:
            validated_data = self._validate_create_data(data)
            if not validated_data["success"]:
                return validated_data
            contribution_plan = ContributionPlan.objects.create(
                **validated_data["data"],
                audit_user=user,
            )
            return vigtra_message(
                success=True,
                message="Contribution plan created successfully",
                data=contribution_plan,
            )
        except Exception as exc:
            logger.error(f"Contribution plan creation failed: {exc}")
            logger.error(traceback.format_exc())
            return vigtra_message(
                message="Contribution plan creation failed",
                data=data,
                error_details=[traceback.format_exc()],
            )

    def _validate_create_data(
        self, data: dict
    ) -> Dict[str, str | dict | list[str] | bool]:
        required_fields = ["name", "plan_type", "calculation_type", "base_amount"]
        for field in required_fields:
            if field not in data:
                return vigtra_message(
                    message=f"Error when creating contribution plan, {field} is required",
                    data=data,
                    error_details=[
                        f"Error when creating contribution plan, {field} is required"
                    ],
                )

        default_auto_generate_code = contribution_plan_config["code_config"][
            "auto_generate"
        ]
        auto_generate_code = data.pop("auto_generate_code", default_auto_generate_code)
        if auto_generate_code:
            data["code"] = generate_contribution_plan_code()
        elif "code" not in data:
            return vigtra_message(
                message="Error when creating contribution plan, code is required if auto_generate_code is False",
                data=data,
                error_details=[
                    "Error when creating contribution plan, code is required if auto_generate_code is False"
                    "auto_generate_code is False and code is not provided"
                ],
            )

        if data["plan_type"] not in [
            plan_type.value for plan_type in ContributionPlanType
        ]:
            valid_plan_types = [plan_type.value for plan_type in ContributionPlanType]
            return vigtra_message(
                message="Error when creating contribution plan, plan_type is invalid",
                data=data,
                error_details=[
                    "Error when creating contribution plan, plan_type is invalid",
                    f"Valid plan types are: {valid_plan_types}",
                ],
            )

        if data["calculation_type"] not in [
            calculation_type.value for calculation_type in ContributionCalculationType
        ]:
            valid_calculation_types = [
                calculation_type.value
                for calculation_type in ContributionCalculationType
            ]
            return vigtra_message(
                message="Error when creating contribution plan, calculation_type is invalid",
                data=data,
                error_details=[
                    "Error when creating contribution plan, calculation_type is invalid",
                    f"Valid calculation types are: {valid_calculation_types}",
                ],
            )

        if data["base_amount"] <= 0:
            return vigtra_message(
                message="Error when creating contribution plan, base_amount must be greater than 0",
                data=data,
                error_details=[
                    "Error when creating contribution plan, base_amount must be greater than 0"
                ],
            )

        if data["contribution_frequency"] not in [
            contribution_frequency.value
            for contribution_frequency in ContributionFrequency
        ]:
            valid_contribution_frequencies = [
                contribution_frequency.value
                for contribution_frequency in ContributionFrequency
            ]
            return vigtra_message(
                message="Error when creating contribution plan, contribution_frequency is invalid",
                data=data,
                error_details=[
                    "Error when creating contribution plan, contribution_frequency is invalid",
                    f"Valid contribution frequencies are: {valid_contribution_frequencies}",
                ],
            )

        if data["status"]:
            status_validation_result = self._validate_create_data_for_status(
                data, data["status"]
            )
            if not status_validation_result["success"]:
                return status_validation_result

        return vigtra_message(
            success=True,
            message="Contribution plan validation successful",
            data=data,
        )

    def _validate_create_data_for_status(
        self, data: dict, status: ContributionPlanStatus
    ) -> Dict[str, str | dict | list[str] | bool]:
        if status != ContributionPlanStatus.DRAFT:
            if "contribution_tired_rates" not in data:
                return vigtra_message(
                    message="Error when creating contribution plan, contribution_tired_rates is required when status is not DRAFT",
                    data=data,
                    error_details=[
                        "Error when creating contribution plan, contribution_tired_rates is required when status is not DRAFT"
                    ],
                )

        if status == ContributionPlanStatus.ACTIVE:
            if "validity_from" not in data:
                return vigtra_message(
                    message="Error when creating contribution plan, validity_from is required when status is ACTIVE",
                    data=data,
                    error_details=[
                        "Error when creating contribution plan, validity_from is required when status is ACTIVE"
                    ],
                )
        elif status == ContributionPlanStatus.INACTIVE:
            if "validity_to" not in data:
                return vigtra_message(
                    message="Error when creating contribution plan, validity_to is required when status is INACTIVE",
                    data=data,
                    error_details=[
                        "Error when creating contribution plan, validity_to is required when status is INACTIVE"
                    ],
                )
        return vigtra_message(
            success=True,
            message="Contribution plan validation successful for status",
            data=data,
        )

    @register_signal("contribution_plan.update_contribution_plan")
    def update_contribution_plan(self, instance: ContributionPlan):
        pass
