from modules.core.gql.core_gql import CreateMutation, UpdateMutation, DeleteMutation
from modules.insurance_plan.models import InsurancePlan
from modules.insurance_plan.services import InsurancePlanService
from modules.core.utils import vigtra_message
import graphene


class CreateInsurancePlanMutation(CreateMutation):
    _mutation_name = "CreateInsurancePlanMutation"
    _mutation_module = "insurance_plan"
    _mutation_model = "InsurancePlan"
    _mutation_action_type = "CREATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        code = graphene.String(description="Insurance plan code")
        name = graphene.String(description="Insurance plan name")
        description = graphene.String(description="Insurance plan description")
        stage = graphene.String(description="Plan stage (N, R, C, E, S, T, X)")
        status = graphene.Int(description="Plan status (1, 2, 4, 8, 16)")
        value = graphene.Decimal(description="Plan value")
        policy_holder_type_id = graphene.ID(
            required=True, description="Content type ID for policy holder"
        )
        policy_holder_id = graphene.String(
            required=True, description="Policy holder ID"
        )
        officer_id = graphene.ID(description="Officer user ID")
        plan_scope_type = graphene.String(description="Plan scope type (L, M, P, S, O)")
        threshold = graphene.Decimal(description="Plan threshold")
        max_members = graphene.Int(description="Maximum number of members")
        recurrence = graphene.Int(description="Recurrence value")
        location_id = graphene.ID(description="Location ID")
        contribution_plan_id = graphene.ID(description="Contribution plan ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = InsurancePlanService.create_insurance_plan(data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class UpdateInsurancePlanMutation(UpdateMutation):
    _mutation_name = "UpdateInsurancePlanMutation"
    _mutation_module = "insurance_plan"
    _mutation_model = "InsurancePlan"
    _mutation_action_type = "UPDATE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Insurance plan ID")
        code = graphene.String(description="New insurance plan code")
        name = graphene.String(description="New insurance plan name")
        description = graphene.String(description="New insurance plan description")
        stage = graphene.String(description="New plan stage")
        status = graphene.Int(description="New plan status")
        value = graphene.Decimal(description="New plan value")
        policy_holder_type_id = graphene.ID(
            description="New content type ID for policy holder"
        )
        policy_holder_id = graphene.String(description="New policy holder ID")
        officer_id = graphene.ID(description="New officer user ID")
        plan_scope_type = graphene.String(description="New plan scope type")
        threshold = graphene.Decimal(description="New plan threshold")
        max_members = graphene.Int(description="New maximum number of members")
        recurrence = graphene.Int(description="New recurrence value")
        location_id = graphene.ID(description="New location ID")
        contribution_plan_id = graphene.ID(description="New contribution plan ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = InsurancePlanService.update_insurance_plan(int(data["id"]), data)
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )


class DeleteInsurancePlanMutation(DeleteMutation):
    _mutation_name = "DeleteInsurancePlanMutation"
    _mutation_module = "insurance_plan"
    _mutation_model = "InsurancePlan"
    _mutation_action_type = "DELETE"
    _mutation_request_result_type = "SUCCESS"

    class Arguments:
        id = graphene.ID(required=True, description="Insurance plan ID")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        result = InsurancePlanService.delete_insurance_plan(int(data["id"]))
        return vigtra_message(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error_details=result.get("error_details", []),
        )
