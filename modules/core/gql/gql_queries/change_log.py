from graphene_django import DjangoObjectType
from modules.core.models.change_log import ChangeLog
import graphene


class ChangeLogGQLType(DjangoObjectType):
    """GraphQL type for ChangeLog with optimized fields and better filtering."""

    # Custom fields with proper resolvers
    action_display = graphene.String(description="Human-readable action description")
    api_type_display = graphene.String(description="Human-readable API type")
    duration_ms = graphene.Float(description="Execution time in milliseconds")
    user_display = graphene.String(description="User display name")

    class Meta:
        model = ChangeLog
        interfaces = (graphene.relay.Node,)

        # Enhanced filtering
        filter_fields = {
            "module": ["exact", "icontains", "in"],
            "model": ["exact", "icontains", "in"],
            "action": ["exact", "in"],
            "api_type": ["exact", "in"],
            "success": ["exact"],
            "user__username": ["exact", "icontains"],
            "timestamp": ["gte", "lte", "gt", "lt"],
            "correlation_id": ["exact"],
            "error_code": ["exact", "in"],
        }

    def resolve_action_display(self, info):
        """Get human-readable action name."""
        return self.get_action_display()

    def resolve_api_type_display(self, info):
        """Get human-readable API type."""
        return self.get_api_type_display()

    def resolve_duration_ms(self, info):
        """Get execution time in milliseconds."""
        return self.duration_ms

    def resolve_user_display(self, info):
        """Get user display name."""
        if self.user:
            return (
                f"{self.user.first_name} {self.user.last_name}".strip()
                or self.user.username
            )
        return None


class ChangeLogQuery(graphene.ObjectType):
    """Queries for ChangeLog with common use cases."""

    change_logs = graphene.relay.ConnectionField(ChangeLogGQLType)
    recent_changes = graphene.List(
        ChangeLogGQLType,
        hours=graphene.Int(default_value=24),
        limit=graphene.Int(default_value=50),
    )
    user_activity = graphene.List(
        ChangeLogGQLType,
        user_id=graphene.Int(required=True),
        days=graphene.Int(default_value=7),
    )

    def resolve_recent_changes(self, info, hours=24, limit=50):
        """Get recent changes within specified hours."""
        return ChangeLog.objects.recent(hours=hours).select_related("user")[:limit]

    def resolve_user_activity(self, info, user_id, days=7):
        """Get activity for a specific user."""
        return (
            ChangeLog.objects.by_user_id(user_id)
            .recent(hours=days * 24)
            .select_related("user")
        )


# Simple stats type for dashboard
class ChangeLogStats(graphene.ObjectType):
    """Simple statistics for ChangeLog dashboard."""

    total_count = graphene.Int()
    success_count = graphene.Int()
    failed_count = graphene.Int()
    success_rate = graphene.Float()


class ChangeLogStatsQuery(graphene.ObjectType):
    """Query for ChangeLog statistics."""

    change_log_stats = graphene.Field(
        ChangeLogStats, days=graphene.Int(default_value=7)
    )

    def resolve_change_log_stats(self, info, days=7):
        """Get basic statistics for the specified period."""
        from django.db.models import Count, Case, When, IntegerField

        queryset = ChangeLog.objects.recent(hours=days * 24)

        stats = queryset.aggregate(
            total=Count("id"),
            successful=Count(
                Case(When(success=True, then=1), output_field=IntegerField())
            ),
            failed=Count(
                Case(When(success=False, then=1), output_field=IntegerField())
            ),
        )

        success_rate = (
            (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
        )

        return ChangeLogStats(
            total_count=stats["total"],
            success_count=stats["successful"],
            failed_count=stats["failed"],
            success_rate=round(success_rate, 2),
        )
