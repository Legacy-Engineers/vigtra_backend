import graphene
from modules.core.models.change_log import ChangeLog
import json


def sanitize_meta(meta):
    safe_meta = {}
    for k, v in meta.items():
        try:
            json.dumps(v)  # check if serializable
            safe_meta[k] = v
        except (TypeError, ValueError):
            continue
    return safe_meta


class CoreMutation(graphene.Mutation):
    """
    Base class for GraphQL mutations with logging functionality.
    Subclasses must implement the `perform_mutation` method.
    """

    _mutation_name: str = None
    _mutation_module: str = None
    _mutation_model: str = None
    _mutation_action_type: str = None
    _mutation_request_result_type = None

    class Arguments:
        pass

    success = graphene.Boolean()
    data = graphene.JSONString()
    message = graphene.String()
    error_details = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        """
        Handles the mutation and logs the change.
        """
        try:
            mutation: dict = cls.perform_mutation(root, info, **data)

            change_log = ChangeLog(
                module=cls._mutation_module,
                model=cls._mutation_model,
                action=cls._mutation_action_type,
                data=mutation.get("data", {}),
                message=mutation.get("message", ""),
                success=mutation.get("success", True),
                error_message=mutation.get("error_details", None),
                api_type=1,
                ip_address=getattr(info.context.META, "REMOTE_ADDR", None),
                user_agent=getattr(info.context.META, "HTTP_USER_AGENT", None),
                user=info.context.user
                if getattr(info.context.user, "is_authenticated", False)
                else None,
                request_header=sanitize_meta(info.context.META),
                object_repr=cls._mutation_name,
                request_result_type=cls._mutation_request_result_type,
            )
            change_log.save()

            return cls(
                success=mutation.get("success", True),
                data=mutation.get("data", {}),
                message=mutation.get("message", ""),
                error_details=mutation.get("error_details", []),
            )
        except Exception as e:
            return cls(
                success=False,
                data=None,
                message="An error occurred during mutation.",
                error_details=[str(e)],
            )

    @classmethod
    def perform_mutation(cls, root, info, **data) -> dict:
        """
        Subclasses must implement this method to perform the actual mutation logic.
        """
        raise NotImplementedError(
            "Subclasses must implement the perform_mutation method"
        )
