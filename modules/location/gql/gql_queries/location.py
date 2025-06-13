from graphene_django import DjangoObjectType
from modules.location.models import Location, HealthFacility, LocationType
import graphene


class LocationGQLType(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = {
            "id": ["exact"],
        }
        interfaces = (graphene.relay.Node,)


class HealthFacilityGQLType(DjangoObjectType):
    class Meta:
        model = HealthFacility
        filter_fields = {
            "id": ["exact"],
        }
        interfaces = (graphene.relay.Node,)


class LocationTypeGQLType(DjangoObjectType):
    class Meta:
        model = LocationType
        filter_fields = {
            "id": ["exact"],
        }
        interfaces = (graphene.relay.Node,)
