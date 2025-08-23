from modules.medical.models.diagnosis import Diagnosis
from graphene_django import DjangoObjectType
import graphene


class DiagnosisGQLType(DjangoObjectType):
    class Meta:
        model = Diagnosis
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "code": ["exact", "icontains"],
            "name": ["exact", "icontains"],
        }
