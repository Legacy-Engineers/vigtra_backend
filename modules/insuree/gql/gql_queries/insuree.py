from graphene_django import DjangoObjectType
import graphene
from ...models import Insuree


class InsureeGQLType(DjangoObjectType):
    class Meta:
        model = Insuree
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "chf_id": ["exact", "icontains"],
        }
