from typing import Dict, Any, Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from modules.insurance_plan.models import (
    InsurancePlan,
    InsurancePlanItem,
    InsurancePlanService,
)
from modules.authentication.models import User
from modules.location.models import Location
from modules.contribution_plan.models import ContributionPlan


class InsurancePlanService:
    """Service class for InsurancePlan operations."""

    @staticmethod
    def create_insurance_plan(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new insurance plan."""
        try:
            with transaction.atomic():
                # Get related objects
                officer = None
                if data.get("officer_id"):
                    officer = User.objects.get(id=data["officer_id"])

                location = None
                if data.get("location_id"):
                    location = Location.objects.get(id=data["location_id"])

                contribution_plan = None
                if data.get("contribution_plan_id"):
                    contribution_plan = ContributionPlan.objects.get(
                        id=data["contribution_plan_id"]
                    )

                # Get policy holder type
                policy_holder_type = ContentType.objects.get(
                    id=data["policy_holder_type_id"]
                )

                insurance_plan = InsurancePlan.objects.create(
                    code=data.get("code"),
                    name=data.get("name"),
                    description=data.get("description"),
                    stage=data.get("stage"),
                    status=data.get("status"),
                    value=data.get("value"),
                    policy_holder_type=policy_holder_type,
                    policy_holder_id=data["policy_holder_id"],
                    officer=officer,
                    plan_scope_type=data.get("plan_scope_type"),
                    threshold=data.get("threshold"),
                    max_members=data.get("max_members"),
                    recurrence=data.get("recurrence"),
                    location=location,
                    contribution_plan=contribution_plan,
                )

                return {
                    "success": True,
                    "data": {
                        "id": insurance_plan.id,
                        "uuid": insurance_plan.uuid,
                        "code": insurance_plan.code,
                        "name": insurance_plan.name,
                        "description": insurance_plan.description,
                        "stage": insurance_plan.stage,
                        "status": insurance_plan.status,
                        "value": float(insurance_plan.value)
                        if insurance_plan.value
                        else None,
                        "policy_holder_type": insurance_plan.policy_holder_type.model
                        if insurance_plan.policy_holder_type
                        else None,
                        "policy_holder_id": insurance_plan.policy_holder_id,
                        "officer": insurance_plan.officer.username
                        if insurance_plan.officer
                        else None,
                        "plan_scope_type": insurance_plan.plan_scope_type,
                        "threshold": float(insurance_plan.threshold)
                        if insurance_plan.threshold
                        else None,
                        "max_members": insurance_plan.max_members,
                        "recurrence": insurance_plan.recurrence,
                        "location": insurance_plan.location.name
                        if insurance_plan.location
                        else None,
                        "contribution_plan": insurance_plan.contribution_plan.name
                        if insurance_plan.contribution_plan
                        else None,
                    },
                    "message": "Insurance plan created successfully",
                }
        except User.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Officer with the specified ID does not exist"],
                "message": "Officer not found",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except ContributionPlan.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Contribution plan with the specified ID does not exist"
                ],
                "message": "Contribution plan not found",
            }
        except ContentType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Content type with the specified ID does not exist"],
                "message": "Content type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to create insurance plan",
            }

    @staticmethod
    def update_insurance_plan(plan_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing insurance plan."""
        try:
            with transaction.atomic():
                insurance_plan = InsurancePlan.objects.get(id=plan_id)

                # Update fields if provided
                if "code" in data:
                    insurance_plan.code = data["code"]
                if "name" in data:
                    insurance_plan.name = data["name"]
                if "description" in data:
                    insurance_plan.description = data["description"]
                if "stage" in data:
                    insurance_plan.stage = data["stage"]
                if "status" in data:
                    insurance_plan.status = data["status"]
                if "value" in data:
                    insurance_plan.value = data["value"]
                if "plan_scope_type" in data:
                    insurance_plan.plan_scope_type = data["plan_scope_type"]
                if "threshold" in data:
                    insurance_plan.threshold = data["threshold"]
                if "max_members" in data:
                    insurance_plan.max_members = data["max_members"]
                if "recurrence" in data:
                    insurance_plan.recurrence = data["recurrence"]

                # Update related objects if provided
                if "officer_id" in data:
                    if data["officer_id"]:
                        officer = User.objects.get(id=data["officer_id"])
                        insurance_plan.officer = officer
                    else:
                        insurance_plan.officer = None

                if "location_id" in data:
                    if data["location_id"]:
                        location = Location.objects.get(id=data["location_id"])
                        insurance_plan.location = location
                    else:
                        insurance_plan.location = None

                if "contribution_plan_id" in data:
                    if data["contribution_plan_id"]:
                        contribution_plan = ContributionPlan.objects.get(
                            id=data["contribution_plan_id"]
                        )
                        insurance_plan.contribution_plan = contribution_plan
                    else:
                        insurance_plan.contribution_plan = None

                if "policy_holder_type_id" in data:
                    policy_holder_type = ContentType.objects.get(
                        id=data["policy_holder_type_id"]
                    )
                    insurance_plan.policy_holder_type = policy_holder_type

                if "policy_holder_id" in data:
                    insurance_plan.policy_holder_id = data["policy_holder_id"]

                insurance_plan.save()

                return {
                    "success": True,
                    "data": {
                        "id": insurance_plan.id,
                        "uuid": insurance_plan.uuid,
                        "code": insurance_plan.code,
                        "name": insurance_plan.name,
                        "description": insurance_plan.description,
                        "stage": insurance_plan.stage,
                        "status": insurance_plan.status,
                        "value": float(insurance_plan.value)
                        if insurance_plan.value
                        else None,
                        "policy_holder_type": insurance_plan.policy_holder_type.model
                        if insurance_plan.policy_holder_type
                        else None,
                        "policy_holder_id": insurance_plan.policy_holder_id,
                        "officer": insurance_plan.officer.username
                        if insurance_plan.officer
                        else None,
                        "plan_scope_type": insurance_plan.plan_scope_type,
                        "threshold": float(insurance_plan.threshold)
                        if insurance_plan.threshold
                        else None,
                        "max_members": insurance_plan.max_members,
                        "recurrence": insurance_plan.recurrence,
                        "location": insurance_plan.location.name
                        if insurance_plan.location
                        else None,
                        "contribution_plan": insurance_plan.contribution_plan.name
                        if insurance_plan.contribution_plan
                        else None,
                    },
                    "message": "Insurance plan updated successfully",
                }
        except InsurancePlan.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Insurance plan with the specified ID does not exist"
                ],
                "message": "Insurance plan not found",
            }
        except User.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Officer with the specified ID does not exist"],
                "message": "Officer not found",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except ContributionPlan.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Contribution plan with the specified ID does not exist"
                ],
                "message": "Contribution plan not found",
            }
        except ContentType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Content type with the specified ID does not exist"],
                "message": "Content type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to update insurance plan",
            }

    @staticmethod
    def delete_insurance_plan(plan_id: int) -> Dict[str, Any]:
        """Delete an insurance plan."""
        try:
            with transaction.atomic():
                insurance_plan = InsurancePlan.objects.get(id=plan_id)

                # Check if plan has items or services
                if (
                    insurance_plan.insuranceplanitem_set.exists()
                    or insurance_plan.insuranceplanservice_set.exists()
                ):
                    return {
                        "success": False,
                        "error_details": [
                            "Insurance plan has items or services and cannot be deleted"
                        ],
                        "message": "Cannot delete insurance plan",
                    }

                insurance_plan.delete()

                return {
                    "success": True,
                    "data": {"id": plan_id},
                    "message": "Insurance plan deleted successfully",
                }
        except InsurancePlan.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Insurance plan with the specified ID does not exist"
                ],
                "message": "Insurance plan not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to delete insurance plan",
            }

    @staticmethod
    def get_plans_by_status(status: int) -> Dict[str, Any]:
        """Get all insurance plans with a specific status."""
        try:
            plans = InsurancePlan.objects.filter(status=status).select_related(
                "officer", "location", "contribution_plan"
            )

            return {
                "success": True,
                "data": {
                    "status": status,
                    "plans": [
                        {
                            "id": plan.id,
                            "code": plan.code,
                            "name": plan.name,
                            "stage": plan.stage,
                            "value": float(plan.value) if plan.value else None,
                            "officer": plan.officer.username if plan.officer else None,
                            "location": plan.location.name if plan.location else None,
                            "contribution_plan": plan.contribution_plan.name
                            if plan.contribution_plan
                            else None,
                        }
                        for plan in plans
                    ],
                    "total_count": plans.count(),
                },
                "message": "Insurance plans retrieved successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to retrieve insurance plans",
            }

    @staticmethod
    def get_plans_by_location(location_id: int) -> Dict[str, Any]:
        """Get all insurance plans in a specific location."""
        try:
            location = Location.objects.get(id=location_id)

            # Get all descendant locations including the current one
            location_ids = location.get_descendants(include_self=True).values_list(
                "id", flat=True
            )

            plans = InsurancePlan.objects.filter(
                location_id__in=location_ids
            ).select_related("officer", "location", "contribution_plan")

            return {
                "success": True,
                "data": {
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "code": location.code,
                    },
                    "plans": [
                        {
                            "id": plan.id,
                            "code": plan.code,
                            "name": plan.name,
                            "stage": plan.stage,
                            "status": plan.status,
                            "value": float(plan.value) if plan.value else None,
                            "officer": plan.officer.username if plan.officer else None,
                            "contribution_plan": plan.contribution_plan.name
                            if plan.contribution_plan
                            else None,
                        }
                        for plan in plans
                    ],
                    "total_count": plans.count(),
                },
                "message": "Insurance plans retrieved successfully",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to retrieve insurance plans",
            }
