from modules.core.gql.core_gql import CoreMutation
import graphene
from modules.core.utils import vigtra_message


class CreateUserMutation(CoreMutation):
    _mutation_name = "CreateUserMutation"
    _mutation_module = "authentication"
    _mutation_action_type = 1
    _mutation_model = "User"

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, root, info, **data) -> dict:
        cls._mutation_request_result_type = 1
        print(data)
        return vigtra_message(data={}, message="Testing", error_details=["error"])
