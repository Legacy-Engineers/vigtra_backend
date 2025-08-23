import graphene
from graphene_django.filter import DjangoFilterConnectionField
from .gql import queries


class Query(graphene.ObjectType):
    claims = DjangoFilterConnectionField(queries.ClaimGQLType)
