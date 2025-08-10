import graphene
from typing import Dict, Any, Optional, List, Union
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
import logging
from abc import ABCMeta, abstractmethod
from modules.core.models.change_log import (
    ChangeLog,
    RequestResultType,
    APIType,
    ActionType,
)
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


def sanitize_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata to ensure JSON serialization compatibility.

    Args:
        meta: Dictionary containing metadata

    Returns:
        Dictionary with only JSON-serializable values
    """
    safe_meta = {}
    for key, value in meta.items():
        try:
            # Test JSON serialization
            json.dumps(value)
            safe_meta[key] = value
        except (TypeError, ValueError, OverflowError):
            # Skip non-serializable values and log for debugging
            logger.debug(
                f"Skipping non-serializable meta key: {key} with value type: {type(value)}"
            )
            continue
    return safe_meta


class MutationResult:
    """Standardized mutation result structure with enhanced features."""

    def __init__(
        self,
        success: bool = True,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
        error_details: Optional[List[str]] = None,
        validation_errors: Optional[Dict[str, List[str]]] = None,
        error_code: Optional[str] = None,
        correlation_id: Optional[str] = None,
        execution_time: Optional[float] = None,
        affected_objects: Optional[List[Dict[str, Any]]] = None,
    ):
        self.success = success
        self.data = data or {}
        self.message = message
        self.error_details = error_details or []
        self.validation_errors = validation_errors or {}
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.execution_time = execution_time
        self.affected_objects = affected_objects or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        result = {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error_details": self.error_details,
        }

        if self.validation_errors:
            result["validation_errors"] = self.validation_errors
        if self.error_code:
            result["error_code"] = self.error_code
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.execution_time is not None:
            result["execution_time"] = self.execution_time
        if self.affected_objects:
            result["affected_objects"] = self.affected_objects

        return result

    def add_affected_object(self, obj_type: str, obj_id: Any, obj_repr: str = None):
        """Add an affected object to the result."""
        self.affected_objects.append(
            {"type": obj_type, "id": obj_id, "repr": obj_repr or str(obj_id)}
        )


# Create a custom metaclass that combines GraphQL and ABC metaclasses
class CoreMutationMeta(type(graphene.Mutation), ABCMeta):
    """Custom metaclass that combines Graphene Mutation and ABC metaclasses."""

    pass


class CoreMutation(graphene.Mutation, metaclass=CoreMutationMeta):
    """
    Enhanced base class for GraphQL mutations with comprehensive logging,
    validation, and error handling functionality.

    Subclasses must implement the `perform_mutation` method and define
    the mutation metadata attributes.
    """

    # Mutation metadata - must be overridden by subclasses
    _mutation_name: str = ""
    _mutation_module: str = ""
    _mutation_model: str = ""
    _mutation_action_type: str = ""
    _mutation_request_result_type: str = ""
    _requires_authentication: bool = True
    _requires_permissions: List[str] = []
    _log_input_data: bool = True  # Whether to log input data
    _log_output_data: bool = True  # Whether to log output data
    _create_correlation_id: bool = False  # Whether to create correlation ID

    class Arguments:
        pass

    # Enhanced response fields
    success = graphene.Boolean(description="Whether the mutation was successful")
    data = graphene.JSONString(description="Mutation result data")
    message = graphene.String(description="Human-readable message")
    error_details = graphene.List(graphene.String, description="List of error details")
    validation_errors = graphene.JSONString(
        description="Field-specific validation errors"
    )
    error_code = graphene.String(description="Machine-readable error code")
    correlation_id = graphene.String(
        description="Correlation ID for tracking related operations"
    )
    execution_time = graphene.Float(description="Execution time in seconds")

    @classmethod
    def mutate(cls, root, info, **input_data):
        """
        Main mutation handler with comprehensive error handling and logging.

        Args:
            root: GraphQL root object
            info: GraphQL info object containing context
            **input_data: Mutation input arguments

        Returns:
            Mutation response with success status and data
        """
        mutation_start_time = timezone.now()
        correlation_id = None

        if cls._create_correlation_id:
            import uuid

            correlation_id = str(uuid.uuid4())

        try:
            # Validate mutation metadata
            cls._validate_mutation_metadata()

            # Perform authentication and authorization checks
            auth_result = cls._check_authentication_and_permissions(info)
            if not auth_result.success:
                auth_result.correlation_id = correlation_id
                cls._log_mutation(
                    info,
                    input_data,
                    auth_result,
                    (timezone.now() - mutation_start_time).total_seconds(),
                )
                return cls._create_response(auth_result)

            # Validate input data
            validation_result = cls._validate_input_data(input_data)
            if not validation_result.success:
                validation_result.correlation_id = correlation_id
                cls._log_mutation(
                    info,
                    input_data,
                    validation_result,
                    (timezone.now() - mutation_start_time).total_seconds(),
                )
                return cls._create_response(validation_result)

            # Execute mutation within transaction
            with transaction.atomic():
                # Set correlation ID in input data for use in perform_mutation
                if correlation_id:
                    input_data["_correlation_id"] = correlation_id

                mutation_result = cls.perform_mutation(root, info, **input_data)

                # Ensure result is a MutationResult object
                if isinstance(mutation_result, dict):
                    mutation_result = MutationResult(**mutation_result)
                elif not isinstance(mutation_result, MutationResult):
                    raise ValueError(
                        "perform_mutation must return MutationResult or dict"
                    )

                # Set correlation ID and execution time
                if correlation_id:
                    mutation_result.correlation_id = correlation_id

                execution_time = (timezone.now() - mutation_start_time).total_seconds()
                mutation_result.execution_time = execution_time

                # Log the mutation
                cls._log_mutation(info, input_data, mutation_result, execution_time)

                return cls._create_response(mutation_result)

        except ValidationError as e:
            execution_time = (timezone.now() - mutation_start_time).total_seconds()
            error_result = MutationResult(
                success=False,
                message="Validation error occurred",
                error_details=[str(e)],
                validation_errors=e.message_dict if hasattr(e, "message_dict") else {},
                error_code="VALIDATION_ERROR",
                correlation_id=correlation_id,
                execution_time=execution_time,
            )
            cls._log_mutation(info, input_data, error_result, execution_time)
            return cls._create_response(error_result)

        except PermissionError as e:
            execution_time = (timezone.now() - mutation_start_time).total_seconds()
            error_result = MutationResult(
                success=False,
                message="Permission denied",
                error_details=[str(e)],
                error_code="PERMISSION_DENIED",
                correlation_id=correlation_id,
                execution_time=execution_time,
            )
            cls._log_mutation(info, input_data, error_result, execution_time)
            return cls._create_response(error_result)

        except Exception as e:
            execution_time = (timezone.now() - mutation_start_time).total_seconds()
            logger.exception(f"Unexpected error in {cls._mutation_name}: {e}")
            error_result = MutationResult(
                success=False,
                message="An unexpected error occurred during mutation",
                error_details=[str(e)],
                error_code="INTERNAL_ERROR",
                correlation_id=correlation_id,
                execution_time=execution_time,
            )
            cls._log_mutation(info, input_data, error_result, execution_time)
            return cls._create_response(error_result)

    @classmethod
    def _validate_mutation_metadata(cls) -> None:
        """Validate that required mutation metadata is defined."""
        required_attrs = [
            "_mutation_name",
            "_mutation_module",
            "_mutation_model",
            "_mutation_action_type",
            "_mutation_request_result_type",
        ]

        missing_attrs = [attr for attr in required_attrs if not getattr(cls, attr)]
        if missing_attrs:
            raise ValueError(
                f"Mutation {cls.__name__} missing required metadata: {missing_attrs}"
            )

    @classmethod
    def _check_authentication_and_permissions(cls, info) -> MutationResult:
        """
        Check authentication and permissions.

        Args:
            info: GraphQL info object

        Returns:
            MutationResult indicating success or failure
        """
        # Check authentication
        if cls._requires_authentication:
            if (
                not hasattr(info.context, "user")
                or not info.context.user.is_authenticated
            ):
                return MutationResult(
                    success=False,
                    message="Authentication required",
                    error_details=["User must be authenticated to perform this action"],
                    error_code="AUTHENTICATION_REQUIRED",
                )

        # Check permissions
        if cls._requires_permissions and hasattr(info.context, "user"):
            user = info.context.user
            missing_permissions = []

            for permission in cls._requires_permissions:
                if not user.has_perm(permission):
                    missing_permissions.append(permission)

            if missing_permissions:
                return MutationResult(
                    success=False,
                    message="Insufficient permissions",
                    error_details=[
                        f"Missing permissions: {', '.join(missing_permissions)}"
                    ],
                    error_code="INSUFFICIENT_PERMISSIONS",
                )

        return MutationResult(success=True)

    @classmethod
    def _validate_input_data(cls, input_data: Dict[str, Any]) -> MutationResult:
        """
        Validate input data. Can be overridden by subclasses for custom validation.

        Args:
            input_data: Input data dictionary

        Returns:
            MutationResult indicating validation success or failure
        """
        # Default implementation - can be overridden by subclasses
        return MutationResult(success=True)

    @classmethod
    def _log_mutation(
        cls,
        info,
        input_data: Dict[str, Any],
        result: MutationResult,
        execution_time: float,
    ) -> None:
        """
        Log mutation execution details using the enhanced ChangeLog model.

        Args:
            info: GraphQL info object
            input_data: Mutation input data
            result: Mutation result
            execution_time: Execution time in seconds
        """
        try:
            # Extract user information
            user = None
            if hasattr(info.context, "user") and info.context.user.is_authenticated:
                user = info.context.user

            # Extract request metadata
            request_meta = getattr(info.context, "META", {})

            # Prepare log data
            log_data = {}
            if cls._log_input_data:
                # Filter out sensitive data and internal fields
                filtered_input = {
                    k: v
                    for k, v in input_data.items()
                    if not k.startswith("_") and k not in ["password", "token"]
                }
                log_data["input"] = filtered_input

            if cls._log_output_data and result.success:
                log_data["output"] = result.data

            log_data["execution_time_seconds"] = execution_time

            # Determine result type
            if result.success:
                request_result_type = RequestResultType.SUCCESS
            elif result.error_code == "AUTHENTICATION_REQUIRED":
                request_result_type = RequestResultType.UNAUTHORIZED
            elif result.error_code == "INSUFFICIENT_PERMISSIONS":
                request_result_type = RequestResultType.FORBIDDEN
            elif result.error_code == "VALIDATION_ERROR":
                request_result_type = RequestResultType.VALIDATION_ERROR
            else:
                request_result_type = RequestResultType.SERVER_ERROR

            # Extract content object information if available
            content_type = None
            object_id = None
            if result.success and result.data:
                # Handle case where result.data is a Django model instance directly
                if hasattr(result.data, "_meta") and hasattr(result.data, "pk"):
                    # result.data is a Django model instance
                    content_type = ContentType.objects.get_for_model(result.data)
                    object_id = result.data.pk
                elif isinstance(result.data, dict):
                    # result.data is a dictionary, look for model instances within it
                    for key, value in result.data.items():
                        if hasattr(value, "_meta") and hasattr(value, "pk"):
                            # This looks like a Django model instance
                            content_type = ContentType.objects.get_for_model(value)
                            object_id = value.pk
                            break
                        elif isinstance(value, dict) and "uuid" in value:
                            # This might be a serialized object with UUID
                            # We'll need to get the actual model instance
                            pass

            # Create change log entry
            ChangeLog.objects.create(
                module=cls._mutation_module,
                model=cls._mutation_model,
                action=cls._mutation_action_type,
                data=log_data,
                object_repr=cls._mutation_name,
                message=result.message or f"{cls._mutation_name} executed",
                success=result.success,
                request_result_type=request_result_type,
                error_message="; ".join(result.error_details)
                if result.error_details
                else None,
                error_code=result.error_code,
                api_type=APIType.GRAPHQL,
                execution_time=execution_time,
                correlation_id=result.correlation_id,
                ip_address=request_meta.get("REMOTE_ADDR"),
                user_agent=request_meta.get("HTTP_USER_AGENT"),
                user=user,
                request_header=sanitize_meta(request_meta),
                session_key=getattr(info.context, "session", {}).get("session_key"),
                content_type=content_type,
                object_id=object_id,
                tags=[
                    cls._mutation_module,
                    cls._mutation_model,
                    cls._mutation_action_type,
                ],
                extra_data={"graphql_field_name": info.field_name}
                if hasattr(info, "field_name")
                else None,
            )

        except Exception as e:
            logger.error(f"Failed to log mutation {cls._mutation_name}: {e}")

    @classmethod
    def _create_response(cls, result: MutationResult):
        """
        Create GraphQL response from MutationResult.

        Args:
            result: MutationResult object

        Returns:
            GraphQL mutation response
        """
        return cls(
            success=result.success,
            data=result.data,
            message=result.message,
            error_details=result.error_details,
            validation_errors=result.validation_errors
            if result.validation_errors
            else None,
            error_code=result.error_code,
            correlation_id=result.correlation_id,
            execution_time=result.execution_time,
        )

    @classmethod
    @abstractmethod
    def perform_mutation(
        cls, root, info, **input_data
    ) -> Union[MutationResult, Dict[str, Any]]:
        """
        Abstract method that subclasses must implement to perform the actual mutation logic.

        Args:
            root: GraphQL root object
            info: GraphQL info object containing context
            **input_data: Mutation input arguments

        Returns:
            MutationResult object or dictionary with mutation results

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            "Subclasses must implement the perform_mutation method"
        )

    @classmethod
    def get_mutation_info(cls) -> Dict[str, Any]:
        """
        Get mutation metadata information.

        Returns:
            Dictionary containing mutation metadata
        """
        return {
            "name": cls._mutation_name,
            "module": cls._mutation_module,
            "model": cls._mutation_model,
            "action_type": cls._mutation_action_type,
            "request_result_type": cls._mutation_request_result_type,
            "requires_authentication": cls._requires_authentication,
            "required_permissions": cls._requires_permissions,
            "logs_input_data": cls._log_input_data,
            "logs_output_data": cls._log_output_data,
            "creates_correlation_id": cls._create_correlation_id,
        }


class CreateMutation(CoreMutation):
    """Base class for create mutations."""

    _mutation_action_type = ActionType.CREATED
    _mutation_request_result_type = RequestResultType.SUCCESS


class UpdateMutation(CoreMutation):
    """Base class for update mutations."""

    _mutation_action_type = ActionType.UPDATED
    _mutation_request_result_type = RequestResultType.SUCCESS


class DeleteMutation(CoreMutation):
    """Base class for delete mutations."""

    _mutation_action_type = ActionType.DELETED
    _mutation_request_result_type = RequestResultType.SUCCESS


class BulkMutation(CoreMutation):
    """Base class for bulk operations."""

    _create_correlation_id = True  # Always create correlation ID for bulk operations

    @classmethod
    def _validate_input_data(cls, input_data: Dict[str, Any]) -> MutationResult:
        """Validate bulk operation constraints."""
        if "items" in input_data:
            items = input_data.get("items", [])
            if not items:
                return MutationResult(
                    success=False,
                    message="No items provided for bulk operation",
                    error_code="EMPTY_BULK_OPERATION",
                )

            # Check bulk operation limits
            max_bulk_size = getattr(cls, "_max_bulk_size", 1000)
            if len(items) > max_bulk_size:
                return MutationResult(
                    success=False,
                    message=f"Bulk operation exceeds maximum size of {max_bulk_size}",
                    error_code="BULK_SIZE_EXCEEDED",
                )

        return MutationResult(success=True)
