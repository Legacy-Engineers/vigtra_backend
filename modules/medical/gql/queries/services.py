from modules.medical.models.service import Service, ServiceCategory
from graphene_django import DjangoObjectType
from modules.core.utils import prefix_filterset
import graphene


class ServiceCategoryGQLType(DjangoObjectType):
    class Meta:
        model = ServiceCategory
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "code": ["exact", "icontains"],
            "name": ["exact", "icontains"],
        }


class ServiceGQLType(DjangoObjectType):
    class Meta:
        model = Service
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "code": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            **prefix_filterset(
                "category__", ServiceCategoryGQLType._meta.filter_fields
            ),
            "care_type": ["exact"],
            "packagetype": ["exact"],
            "manualPrice": ["exact"],
            "level": ["exact"],
            "price": ["exact", "gte", "lte"],
            "maximum_amount": ["exact", "gte", "lte"],
            "frequency": ["exact", "gte", "lte"],
        }
