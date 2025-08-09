from graphene_django import DjangoObjectType
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent
import graphene


class CRUDEventGQLType(DjangoObjectType):
    class Meta:
        model = CRUDEvent
        interfaces = (graphene.relay.Node,)


class LoginEventGQLType(DjangoObjectType):
    class Meta:
        model = LoginEvent
        interfaces = (graphene.relay.Node,)


class RequestEventGQLType(DjangoObjectType):
    class Meta:
        model = RequestEvent
        interfaces = (graphene.relay.Node,)
