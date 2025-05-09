from graphene_django import DjangoObjectType
from ...models import User
import graphene


class UserGQLType(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "username": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "created_at": ["exact"],
            "updated_at": ["exact"],
            "user_permissions": ["exact"],
        }
