from graphene_django import DjangoObjectType
from modules.insurance_coverage.models import Coverage
import graphene


class CoverageGQLType(DjangoObjectType):
    class Meta:
        model = Coverage
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "insurance_plan": ["exact"],
            "policy_holder_id": ["exact"],
            "payor_id": ["exact"],
            "status": ["exact"],
            "start_date": ["exact", "gte", "lte"],
            "end_date": ["exact", "gte", "lte"],
        }
