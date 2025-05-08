from graphene_django import DjangoObjectType
from django.contrib.auth.models import Group
import graphene


class GroupGQLType(DjangoObjectType):

    class Meta:
        model = Group
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["exact", "icontains"],
            "permissions__name": ["exact", "icontains"],
        }
