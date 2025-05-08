from graphene_django import DjangoObjectType
from django.contrib.auth.models import Permission
import graphene

class PermissionGQLType(DjangoObjectType):
    class Meta:
        model = Permission
        filter_fields = {
            "name": ["exact", "icontains"],
            "codename": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)