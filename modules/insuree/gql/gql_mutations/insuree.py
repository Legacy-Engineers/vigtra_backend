from modules.core.gql.core_gql import CoreMutation
import graphene


class CreateInsureeMutation(CoreMutation):
    """
    Mutation to create an Insuree.
    """

    _mutation_name = "CreateInsureeMutation"
    _mutation_module = "insuree"
    _mutation_model = "Insuree"
    _mutation_action_type = 1

    class Arguements:
        name = graphene.String(required=True)
        age = graphene.Int(required=True)

    def perform_mutation(self, root, info, **data):
        return {
            "data": {"id": 1, "name": data.get("name")},
            "message": "Insuree created successfully",
            "success": True,
        }
