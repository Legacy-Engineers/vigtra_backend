from graphene_django import DjangoObjectType
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent
import graphene


class CRUDEventGQLType(DjangoObjectType):
    class Meta:
        model = CRUDEvent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "user": ["exact"],
            "datetime": ["exact", "gte", "lte"],
            "event_type": ["exact"],
        }


class LoginEventGQLType(DjangoObjectType):
    class Meta:
        model = LoginEvent
        filter_fields = {
            "user": ["exact"],
            "datetime": ["exact", "gte", "lte"],
            "remote_ip": ["exact"],
            "username": ["exact"],
            "login_type": ["exact"],
        }
        interfaces = (graphene.relay.Node,)


class RequestEventGQLType(DjangoObjectType):
    class Meta:
        model = RequestEvent
        filter_fields = {
            "user": ["exact"],
            "datetime": ["exact", "gte", "lte"],
            "remote_ip": ["exact"],
            "method": ["exact"],
            "url": ["exact"],
            "query_string": ["exact"],
        }
        interfaces = (graphene.relay.Node,)
