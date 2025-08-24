from modules.core.gql.core_gql import CreateMutation, UpdateMutation, DeleteMutation
from modules.location.models import Location, LocationType
from modules.location.services import LocationService
from modules.core.utils import vigtra_message
import graphene


class CreateLocationTypeMutation(CreateMutation):
    _mutation_name = "CreateLocationTypeMutation"
    _mutation_module = "location"
    _mutation_model = "LocationType"
    _mutation_action_type = "CREATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        name = graphene.String(required=True, description="Name of the location type")
        level = graphene.Int(
            required=True, description="Hierarchy level (1 for highest)"
        )

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.create_location_type(data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class UpdateLocationTypeMutation(UpdateMutation):
    _mutation_name = "UpdateLocationTypeMutation"
    _mutation_module = "location"
    _mutation_model = "LocationType"
    _mutation_action_type = "UPDATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Location type ID")
        name = graphene.String(description="New name for the location type")
        level = graphene.Int(description="New hierarchy level")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.update_location_type(int(data["id"]), data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class DeleteLocationTypeMutation(DeleteMutation):
    _mutation_name = "DeleteLocationTypeMutation"
    _mutation_module = "location"
    _mutation_model = "LocationType"
    _mutation_action_type = "DELETE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Location type ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.delete_location_type(int(data["id"]))
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class CreateLocationMutation(CreateMutation):
    _mutation_name = "CreateLocationMutation"
    _mutation_module = "location"
    _mutation_model = "Location"
    _mutation_action_type = "CREATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        name = graphene.String(required=True, description="Name of the location")
        type_id = graphene.ID(required=True, description="Location type ID")
        parent_id = graphene.ID(description="Parent location ID (optional)")
        code = graphene.String(description="Optional unique code for the location")
        is_active = graphene.Boolean(description="Whether the location is active")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.create_location(data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class UpdateLocationMutation(UpdateMutation):
    _mutation_name = "UpdateLocationMutation"
    _mutation_module = "location"
    _mutation_model = "Location"
    _mutation_action_type = "UPDATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Location ID")
        name = graphene.String(description="New name for the location")
        type_id = graphene.ID(description="New location type ID")
        parent_id = graphene.ID(description="New parent location ID")
        code = graphene.String(description="New code for the location")
        is_active = graphene.Boolean(description="New active status")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.update_location(int(data["id"]), data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class DeleteLocationMutation(DeleteMutation):
    _mutation_name = "DeleteLocationMutation"
    _mutation_module = "location"
    _mutation_model = "Location"
    _mutation_action_type = "DELETE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Location ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = LocationService.delete_location(int(data["id"]))
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )
