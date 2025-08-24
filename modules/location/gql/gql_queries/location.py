from graphene_django import DjangoObjectType
from modules.location.models import Location, LocationType
from modules.core.utils import prefix_filterset
import graphene


class LocationGQLType(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "code": ["exact", "icontains"],
            "is_active": ["exact"],
            "type__name": ["exact", "icontains"],
            "type__level": ["exact", "gte", "lte"],
            "parent__name": ["exact", "icontains"],
            "created_at": ["exact", "gte", "lte"],
            "updated_at": ["exact", "gte", "lte"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields for hierarchical data
    full_path = graphene.String(description="Full hierarchical path of the location")
    child_count = graphene.Int(description="Number of direct children")
    descendant_count = graphene.Int(description="Total number of descendants")
    level = graphene.Int(description="Hierarchy level")

    def resolve_full_path(self, info):
        return self.get_full_path()

    def resolve_child_count(self, info):
        return self.child_count

    def resolve_descendant_count(self, info):
        return self.descendant_count

    def resolve_level(self, info):
        return self.level


class LocationTypeGQLType(DjangoObjectType):
    class Meta:
        model = LocationType
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "level": ["exact", "gte", "lte"],
            "created_at": ["exact", "gte", "lte"],
            "updated_at": ["exact", "gte", "lte"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    location_count = graphene.Int(description="Number of locations using this type")

    def resolve_location_count(self, info):
        return self.location_set.count()
