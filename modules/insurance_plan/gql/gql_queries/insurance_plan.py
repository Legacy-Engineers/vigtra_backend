from graphene_django import DjangoObjectType
from modules.insurance_plan.models import (
    InsurancePlan,
    InsurancePlanItem,
    InsurancePlanService,
)
from modules.core.utils import prefix_filterset
import graphene


class InsurancePlanGQLType(DjangoObjectType):
    class Meta:
        model = InsurancePlan
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "code": ["exact", "icontains", "istartswith"],
            "name": ["exact", "icontains", "istartswith"],
            "stage": ["exact"],
            "status": ["exact"],
            "value": ["exact", "gte", "lte"],
            "plan_scope_type": ["exact"],
            "threshold": ["exact", "gte", "lte"],
            "max_members": ["exact", "gte", "lte"],
            "recurrence": ["exact", "gte", "lte"],
            "location__name": ["exact", "icontains"],
            "location__code": ["exact", "icontains"],
            "contribution_plan__name": ["exact", "icontains"],
            "officer__username": ["exact", "icontains"],
            "officer__email": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    policy_holder_type_name = graphene.String(
        description="Name of the policy holder type"
    )
    policy_holder_repr = graphene.String(
        description="String representation of policy holder"
    )
    stage_display = graphene.String(description="Human-readable stage name")
    status_display = graphene.String(description="Human-readable status name")
    scope_type_display = graphene.String(description="Human-readable scope type name")

    def resolve_policy_holder_type_name(self, info):
        return self.policy_holder_type.model if self.policy_holder_type else None

    def resolve_policy_holder_repr(self, info):
        return str(self.policy_holder) if self.policy_holder else None

    def resolve_stage_display(self, info):
        return self.get_stage_display() if self.stage else None

    def resolve_status_display(self, info):
        return self.get_status_display() if self.status else None

    def resolve_scope_type_display(self, info):
        return self.get_plan_scope_type_display() if self.plan_scope_type else None


class InsurancePlanItemGQLType(DjangoObjectType):
    class Meta:
        model = InsurancePlanItem
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "insurance_plan__code": ["exact", "icontains"],
            "insurance_plan__name": ["exact", "icontains"],
            "item__name": ["exact", "icontains"],
            "quantity": ["exact", "gte", "lte"],
            "unit_price": ["exact", "gte", "lte"],
            "total_price": ["exact", "gte", "lte"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    item_name = graphene.String(description="Name of the item")

    def resolve_item_name(self, info):
        return self.item.name if self.item else None


class InsurancePlanServiceGQLType(DjangoObjectType):
    class Meta:
        model = InsurancePlanService
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "insurance_plan__code": ["exact", "icontains"],
            "insurance_plan__name": ["exact", "icontains"],
            "service__name": ["exact", "icontains"],
            "quantity": ["exact", "gte", "lte"],
            "unit_price": ["exact", "gte", "lte"],
            "total_price": ["exact", "gte", "lte"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    service_name = graphene.String(description="Name of the service")

    def resolve_service_name(self, info):
        return self.service.name if self.service else None
