from graphene_django import DjangoObjectType
from modules.claim.models import Claim
from modules.core.utils import prefix_filterset
from modules.location.gql.gql_queries.health_facility import HealthFacilityGQLType
from modules.medical.gql.queries.diagnosis import DiagnosisGQLType
import graphene


class ClaimGQLType(DjangoObjectType):
    class Meta:
        model = Claim
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "code": ["exact", "icontains"],
            "insuree": ["exact"],
            **prefix_filterset(
                "health_facility__", HealthFacilityGQLType._meta.filter_fields
            ),
            "claim_date": ["exact", "gte", "lte"],
            "visit_type": ["exact"],
            **prefix_filterset("diagnosis__", DiagnosisGQLType._meta.filter_fields),
            "status": ["exact"],
            "total_amount": ["exact", "gte", "lte"],
            "explanation": ["exact", "icontains"],
            "created_at": ["exact", "gte", "lte"],
        }
