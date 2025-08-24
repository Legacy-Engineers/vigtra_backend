from graphene_django import DjangoObjectType
from modules.formal_sector.models import FormalSector
import graphene


class FormalSectorGQLType(DjangoObjectType):
    class Meta:
        model = FormalSector
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "code": ["exact", "icontains"],
            "trade_name": ["exact", "icontains"],
            "sector_type": ["exact"],
            "sector_type_other": ["exact", "icontains"],
            "location": ["exact"],
            "address": ["exact", "icontains"],
            "phone": ["exact", "icontains"],
            "fax": ["exact", "icontains"],
            "email": ["exact", "icontains"],
        }
