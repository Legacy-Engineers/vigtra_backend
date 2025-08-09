from graphene_django import DjangoObjectType
from modules.location.models import HealthFacility
from modules.core.utils import prefix_filterset
from .location import LocationGQLType
import graphene


class HealthFacilityGQLType(DjangoObjectType):
    class Meta:
        model = HealthFacility
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
            "code": ["exact", "icontains"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        interfaces = (graphene.relay.Node,)
