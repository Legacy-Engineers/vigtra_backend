from modules.core.gql.core_gql import CoreMutation
import graphene


class FamilyInput(graphene.InputObjectType):
    head_insuree_uuid = graphene.String(required=True)
    location_uuid = graphene.String()
    family_type_code = graphene.String()

    address = graphene.String()
    is_offline = graphene.String()
    ethnicity = graphene.String()
    confirmation_no = graphene.String()

    poverty = graphene.Boolean(default=False)


class CreateFamilyMutation(CoreMutation):
    _mutation_name = "CreateFamilyMutation"
    _mutation_module = "insuree"
    _mutation_model = "Insuree"

    class Arguments:
        input = FamilyInput(required=True)
