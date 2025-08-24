from graphene_django import DjangoObjectType
from modules.location.models import HealthFacility, HealthFacilityType
from modules.core.utils import prefix_filterset
from .location import LocationGQLType
import graphene


class HealthFacilityGQLType(DjangoObjectType):
    class Meta:
        model = HealthFacility
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "code": ["exact", "icontains"],
            "is_active": ["exact"],
            "facility_type__name": ["exact", "icontains"],
            "location__name": ["exact", "icontains"],
            "location__code": ["exact", "icontains"],
            "phone": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "established_date": ["exact", "gte", "lte"],
            "created_date": ["exact", "gte", "lte"],
            "last_modified": ["exact", "gte", "lte"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    full_address = graphene.String(
        description="Complete address including location hierarchy"
    )
    display_name = graphene.String(description="Display-friendly name with location")

    def resolve_full_address(self, info):
        return self.full_address

    def resolve_display_name(self, info):
        return self.display_name


class HealthFacilityTypeGQLType(DjangoObjectType):
    class Meta:
        model = HealthFacilityType
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "is_active": ["exact"],
            "created_at": ["exact", "gte", "lte"],
            "updated_at": ["exact", "gte", "lte"],
        }

    # Custom fields
    facility_count = graphene.Int(
        description="Number of health facilities using this type"
    )

    def resolve_facility_count(self, info):
        return self.healthfacility_set.count()
