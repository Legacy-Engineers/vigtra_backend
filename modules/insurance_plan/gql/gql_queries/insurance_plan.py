from graphene_django import DjangoObjectType
from modules.insurance_plan.models import InsurancePlan
import graphene


class InsurancePlanGQLType(DjangoObjectType):
    class Meta:
        model = InsurancePlan
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
