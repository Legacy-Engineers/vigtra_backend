from graphene_django import DjangoObjectType
from modules.formal_sector.models import FormalSectorInsuree
import graphene


class FormalSectorInsureeGQLType(DjangoObjectType):
    class Meta:
        model = FormalSectorInsuree
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "formal_sector": ["exact"],
            "insuree": ["exact"],
            "contribution_plan_bundle": ["exact"],
        }
