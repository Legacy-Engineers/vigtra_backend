from modules.core.gql.core_gql import CreateMutation
import graphene
from modules.core.utils import vigtra_message


class CreateUserMutation(CreateMutation):
    _mutation_name = "CreateUserMutation"
    _mutation_module = "authentication"
    _mutation_model = "User"

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, root, info, **data) -> dict:
        print(data)
        return vigtra_message(data={}, message="Testing", error_details=["error"])
