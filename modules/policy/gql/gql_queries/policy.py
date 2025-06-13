from graphene_django import DjangoObjectType
from modules.policy.models import Policy
import graphene


class PolicyGQLType(DjangoObjectType):
    class Meta:
        model = Policy
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact", "in"],
            "uuid": ["exact", "icontains"],
            "stage": ["exact", "icontains"],
            "status": ["exact", "in"],
            "value": ["exact", "gte", "lte"],
            "enroll_date": ["exact", "gte", "lte"],
            "start_date": ["exact", "gte", "lte"],
            "effective_date": ["exact", "gte", "lte"],
            "expiry_date": ["exact", "gte", "lte"],
        }
