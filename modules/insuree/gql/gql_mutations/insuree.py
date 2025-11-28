from modules.core.gql.core_gql import CreateMutation
from modules.insuree.services.insuree import InsureeService
from modules.core.utils import vigtra_message
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
    chf_id = graphene.String()
    auto_generate_chf_id = graphene.Boolean()
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
    notes = graphene.String()
    identification_number = graphene.String()
    identification_type_code = graphene.String()
    profession_code = graphene.String()
    education_code = graphene.String()
    relation_code = graphene.String()


class CreateInsureeMutation(CreateMutation):
    """
    Mutation to create an Insuree.
    """

    _mutation_name = "CreateInsureeMutation"
    _mutation_module = "insuree"
    _mutation_model = "Insuree"

    class Arguments:
        input = CreateInsureeInput(required=True)

    @classmethod
    def perform_mutation(cls, user, root, info, **data):
        auto_generate_chf_id = data.get("auto_generate_chf_id", True)
        if not auto_generate_chf_id:
            if not data.get("chf_id"):
                return vigtra_message(
                    message="CHF ID is required if auto_generate_chf_id is False",
                    data=data,
                )

        return INSUREE_SERVICE.create_insuree(data, user=user)
