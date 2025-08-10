from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from modules.authentication.models import User
import uuid


class ActionType(models.TextChoices):
    """Enumeration of possible actions that can be logged."""

    # CRUD Operations
    CREATED = "CREATE", "Created"
    UPDATED = "UPDATE", "Updated"
    DELETED = "DELETE", "Deleted"
    RESTORED = "RESTORE", "Restored"

    # State Management
    ARCHIVED = "ARCHIVE", "Archived"
    UNARCHIVED = "UNARCHIVE", "Unarchived"
    ACTIVATED = "ACTIVATE", "Activated"
    DEACTIVATED = "DEACTIVATE", "Deactivated"

    # Data Operations
    IMPORTED = "IMPORT", "Imported"
    EXPORTED = "EXPORT", "Exported"
    SYNCED = "SYNC", "Synced"
    MERGED = "MERGE", "Merged"
    SPLIT = "SPLIT", "Split"
    MIGRATED = "MIGRATE", "Migrated"

    # Workflow Actions
    APPROVED = "APPROVE", "Approved"
    REJECTED = "REJECT", "Rejected"
    CANCELLED = "CANCEL", "Cancelled"
    COMPLETED = "COMPLETE", "Completed"
    FAILED = "FAIL", "Failed"

    # Process Control
    STARTED = "START", "Started"
    PAUSED = "PAUSE", "Paused"
    RESUMED = "RESUME", "Resumed"
    STOPPED = "STOP", "Stopped"
    RESTARTED = "RESTART", "Restarted"

    # Scheduling
    SCHEDULED = "SCHEDULE", "Scheduled"
    UNSCHEDULED = "UNSCHEDULE", "Unscheduled"
    RESCHEDULED = "RESCHEDULE", "Rescheduled"

    # Security
    LOCKED = "LOCK", "Locked"
    UNLOCKED = "UNLOCK", "Unlocked"
    VERIFIED = "VERIFY", "Verified"
    UNVERIFIED = "UNVERIFY", "Unverified"

    # Content Management
    PUBLISHED = "PUBLISH", "Published"
    UNPUBLISHED = "UNPUBLISH", "Unpublished"
    DRAFTED = "DRAFT", "Drafted"
    SUBMITTED = "SUBMIT", "Submitted"

    # Authentication
    LOGIN = "LOGIN", "Logged In"
    LOGOUT = "LOGOUT", "Logged Out"
    PASSWORD_RESET = "PWD_RESET", "Password Reset"

    # Custom Actions
    CUSTOM = "CUSTOM", "Custom Action"


class RequestResultType(models.TextChoices):
    """HTTP-like response status categories."""

    SUCCESS = "SUCCESS", "Successful"
    CLIENT_ERROR = "CLIENT_ERR", "Client Error"
    SERVER_ERROR = "SERVER_ERR", "Server Error"
    UNAUTHORIZED = "UNAUTH", "Unauthorized"
    FORBIDDEN = "FORBIDDEN", "Forbidden"
    NOT_FOUND = "NOT_FOUND", "Not Found"
    CONFLICT = "CONFLICT", "Conflict"
    VALIDATION_ERROR = "VALID_ERR", "Validation Error"
    TIMEOUT = "TIMEOUT", "Timeout"
    RATE_LIMITED = "RATE_LIMIT", "Rate Limited"


class APIType(models.TextChoices):
    """API interface types."""

    GRAPHQL = "GQL", "GraphQL"
    REST = "REST", "REST API"
    WEB = "WEB", "Web Interface"
    CLI = "CLI", "Command Line"
    WEBHOOK = "WEBHOOK", "Webhook"
    BACKGROUND = "BG", "Background Task"


class ChangeLogQuerySet(models.QuerySet):
    """Custom QuerySet for ChangeLog with useful filtering methods."""

    def successful(self):
        """Filter to successful operations only."""
        return self.filter(success=True)

    def failed(self):
        """Filter to failed operations only."""
        return self.filter(success=False)

    def by_user(self, user):
        """Filter by specific user."""
        return self.filter(user=user)

    def by_module(self, module):
        """Filter by module."""
        return self.filter(module=module)

    def by_action(self, action):
        """Filter by action type."""
        return self.filter(action=action)

    def recent(self, hours=24):
        """Filter to recent entries within specified hours."""
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(timestamp__gte=cutoff_time)

    def for_object(self, obj):
        """Filter logs for a specific object instance."""
        return self.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk
        )


class ChangeLogManager(models.Manager):
    """Custom manager for ChangeLog."""

    def get_queryset(self):
        return ChangeLogQuerySet(self.model, using=self._db)

    def successful(self):
        return self.get_queryset().successful()

    def failed(self):
        return self.get_queryset().failed()

    def by_user(self, user):
        return self.get_queryset().by_user(user)

    def by_module(self, module):
        return self.get_queryset().by_module(module)

    def recent(self, hours=24):
        return self.get_queryset().recent(hours)

    def for_object(self, obj):
        return self.get_queryset().for_object(obj)


class ChangeLog(models.Model):
    """
    Enhanced change log model for comprehensive audit trail tracking.

    This model tracks all significant changes and actions across the system,
    providing a complete audit trail for compliance and debugging purposes.
    """

    # Core identification
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Action details
    module = models.CharField(
        max_length=50,
        help_text="Module or app where the action occurred",
        db_index=True,
    )
    model = models.CharField(
        max_length=50, help_text="Model or entity affected", db_index=True
    )
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        help_text="Type of action performed",
        db_index=True,
    )

    # Generic foreign key to the affected object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Content type of the affected object",
    )
    object_id = models.PositiveIntegerField(
        null=True, blank=True, help_text="ID of the affected object"
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Data and context
    data = models.JSONField(
        null=True, blank=True, help_text="Serialized data related to the action"
    )
    object_repr = models.CharField(
        max_length=500, help_text="String representation of the affected object"
    )
    message = models.TextField(help_text="Human-readable description of the action")

    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When the action occurred"
    )
    correlation_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID to correlate related actions",
        db_index=True,
    )

    # User and request context
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who performed the action",
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of the request"
    )
    user_agent = models.TextField(
        null=True, blank=True, help_text="User agent string from the request"
    )
    request_header = models.JSONField(
        null=True, blank=True, help_text="Sanitized request headers"
    )
    session_key = models.CharField(
        max_length=40, null=True, blank=True, help_text="Session key for web requests"
    )

    # Result tracking
    success = models.BooleanField(
        default=True, db_index=True, help_text="Whether the action was successful"
    )
    request_result_type = models.CharField(
        max_length=15,
        choices=RequestResultType.choices,
        null=True,
        blank=True,
        help_text="Classification of the result",
    )
    error_message = models.TextField(
        null=True, blank=True, help_text="Error message if the action failed"
    )
    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Error code if the action failed",
    )

    # API context
    api_type = models.CharField(
        max_length=10,
        choices=APIType.choices,
        default=APIType.WEB,
        help_text="Type of API interface used",
    )

    # Performance metrics
    execution_time = models.FloatField(
        null=True, blank=True, help_text="Execution time in seconds"
    )

    # Additional context
    tags = models.JSONField(
        default=list, help_text="Tags for categorization and filtering"
    )
    extra_data = models.JSONField(
        null=True, blank=True, help_text="Additional context-specific data"
    )

    objects = ChangeLogManager()

    class Meta:
        verbose_name = "Change Log"
        verbose_name_plural = "Change Logs"
        ordering = ["-timestamp"]
        db_table = "tblChangeLogs"
        indexes = [
            models.Index(fields=["module", "model"], name="idx_changelog_module_model"),
            models.Index(
                fields=["action", "timestamp"], name="idx_changelog_action_time"
            ),
            models.Index(fields=["user", "timestamp"], name="idx_changelog_user_time"),
            models.Index(
                fields=["success", "timestamp"], name="idx_changelog_success_time"
            ),
            models.Index(fields=["correlation_id"], name="idx_changelog_correlation"),
            models.Index(
                fields=["content_type", "object_id"], name="idx_changelog_content"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(execution_time__gte=0),
                name="chk_changelog_positive_execution_time",
            )
        ]

    def __str__(self):
        return f"{self.module}.{self.model} - {self.get_action_display()} at {self.timestamp}"

    @property
    def duration_ms(self):
        """Get execution time in milliseconds."""
        return self.execution_time * 1000 if self.execution_time else None

    def get_related_logs(self):
        """Get logs with the same correlation ID."""
        if self.correlation_id:
            return ChangeLog.objects.filter(correlation_id=self.correlation_id).exclude(
                id=self.id
            )
        return ChangeLog.objects.none()

    @classmethod
    def log_action(
        cls,
        module,
        model,
        action,
        user=None,
        object_instance=None,
        data=None,
        message="",
        success=True,
        api_type=APIType.WEB,
        correlation_id=None,
        tags=None,
        **kwargs,
    ):
        """
        Convenience method to create a change log entry.

        Args:
            module: Module name
            model: Model name
            action: Action type
            user: User performing the action
            object_instance: The affected object instance
            data: Additional data to log
            message: Human-readable message
            success: Whether the action was successful
            api_type: API type used
            correlation_id: Correlation ID for related actions
            tags: List of tags
            **kwargs: Additional fields
        """
        log_data = {
            "module": module,
            "model": model,
            "action": action,
            "user": user,
            "data": data,
            "message": message,
            "success": success,
            "api_type": api_type,
            "correlation_id": correlation_id,
            "tags": tags or [],
        }

        if object_instance:
            # Set content_type and object_id for the GenericForeignKey
            from django.contrib.contenttypes.models import ContentType

            content_type = ContentType.objects.get_for_model(object_instance)
            log_data.update(
                {
                    "content_type": content_type,
                    "object_id": object_instance.pk,
                    "object_repr": str(object_instance),
                }
            )

        log_data.update(kwargs)

        return cls.objects.create(**log_data)
