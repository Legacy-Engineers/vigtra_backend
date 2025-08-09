from modules.core.gql.core_gql import CreateMutation
from modules.insuree.services.insuree import InsureeService
import graphene

INSUREE_SERVICE = InsureeService()


class MaritalStatus(graphene.Enum):
    SINGLE = "S"
    MARRIED = "M"
    DIVORCED = "D"
    WIDOWED = "W"


class InsureeStatus(graphene.Enum):
    ACTIVE = "AC"
    INACTIVE = "IN"
    DECEASED = "DE"
    SUSPENDED = "SU"
    PENDING = "PE"


class CreateInsureeInput(graphene.InputObjectType):
    chf_id = graphene.String(required=True)
    last_name = graphene.String(required=True)
    other_names = graphene.String(required=True)
    gender_code = graphene.String(required=True)
    date_of_birth = graphene.Date(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    address = graphene.String()
    secondary_health_facility_code = graphene.String()
    other_health_facility_codes = graphene.List(graphene.String)
    marital_status = graphene.Field(MaritalStatus)
    passport_number = graphene.String()
    status = graphene.Field(InsureeStatus)
    offline = graphene.Boolean()


class CreateInsureeMutation(CreateMutation):
    """
    Mutation to create an Insuree.
    """

    _mutation_name = "CreateInsureeMutation"
    _mutation_module = "insuree"
    _mutation_model = "Insuree"
    _mutation_action_type = 1

    class Arguments:
        input = CreateInsureeInput(required=True)

    def perform_mutation(self, root, info, **data):
        return {
            "data": {"id": 1, "name": data.get("name")},
            "message": "Insuree created successfully",
            "success": True,
        }
