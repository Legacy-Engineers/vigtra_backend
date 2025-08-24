from modules.core.gql.core_gql import CreateMutation, UpdateMutation, DeleteMutation
from modules.location.models import HealthFacility, HealthFacilityType
from modules.location.services import HealthFacilityService
from modules.core.utils import vigtra_message
import graphene


class CreateHealthFacilityTypeMutation(CreateMutation):
    _mutation_name = "CreateHealthFacilityTypeMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacilityType"
    _mutation_action_type = "CREATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        name = graphene.String(
            required=True, description="Name of the health facility type"
        )
        description = graphene.String(description="Description of the facility type")
        is_active = graphene.Boolean(description="Whether the facility type is active")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.create_health_facility_type(data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class UpdateHealthFacilityTypeMutation(UpdateMutation):
    _mutation_name = "UpdateHealthFacilityTypeMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacilityType"
    _mutation_action_type = "UPDATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Health facility type ID")
        name = graphene.String(description="New name for the facility type")
        description = graphene.String(
            description="New description for the facility type"
        )
        is_active = graphene.Boolean(description="New active status")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.update_health_facility_type(
            int(data["id"]), data
        )
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class DeleteHealthFacilityTypeMutation(DeleteMutation):
    _mutation_name = "DeleteHealthFacilityTypeMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacilityType"
    _mutation_action_type = "DELETE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Health facility type ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.delete_health_facility_type(int(data["id"]))
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class CreateHealthFacilityMutation(CreateMutation):
    _mutation_name = "CreateHealthFacilityMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacility"
    _mutation_action_type = "CREATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        code = graphene.String(required=True, description="Unique facility code")
        name = graphene.String(required=True, description="Facility name")
        facility_type_id = graphene.ID(required=True, description="Facility type ID")
        location_id = graphene.ID(required=True, description="Location ID")
        description = graphene.String(description="Facility description")
        address = graphene.String(description="Physical address")
        phone = graphene.String(description="Phone number")
        email = graphene.String(description="Email address")
        is_active = graphene.Boolean(description="Whether the facility is active")
        established_date = graphene.Date(
            description="Date when facility was established"
        )

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.create_health_facility(data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class UpdateHealthFacilityMutation(UpdateMutation):
    _mutation_name = "UpdateHealthFacilityMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacility"
    _mutation_action_type = "UPDATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Health facility ID")
        code = graphene.String(description="New facility code")
        name = graphene.String(description="New facility name")
        facility_type_id = graphene.ID(description="New facility type ID")
        location_id = graphene.ID(description="New location ID")
        description = graphene.String(description="New facility description")
        address = graphene.String(description="New physical address")
        phone = graphene.String(description="New phone number")
        email = graphene.String(description="New email address")
        is_active = graphene.Boolean(description="New active status")
        established_date = graphene.Date(description="New established date")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.update_health_facility(int(data["id"]), data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class DeleteHealthFacilityMutation(DeleteMutation):
    _mutation_name = "DeleteHealthFacilityMutation"
    _mutation_module = "location"
    _mutation_model = "HealthFacility"
    _mutation_action_type = "DELETE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Health facility ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = HealthFacilityService.delete_health_facility(int(data["id"]))
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )
