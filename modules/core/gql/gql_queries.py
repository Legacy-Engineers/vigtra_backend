from graphene_django import DjangoObjectType
from ..models.change_log import ChangeLog
import graphene


class ChangeLogGQLType(DjangoObjectType):
    api_type = graphene.Int()
    action = graphene.Int()

    class Meta:
        model = ChangeLog
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "module": ["exact", "icontains", "istartswith", "in"],
            "model": ["exact", "icontains", "istartswith", "in"],
            "action": ["exact", "icontains", "in"],
            "api_type": ["exact", "icontains", "in"],
            "user__username": ["exact", "icontains", "istartswith", "in"],
            "timestamp": ["exact", "gte", "lte", "gt", "lt"],
        }
