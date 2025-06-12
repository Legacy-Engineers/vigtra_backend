from graphene_django.filter import DjangoFilterConnectionField
from .gql import gql_queries
import graphene


class Query(graphene.ObjectType):
    insurees = DjangoFilterConnectionField(gql_queries.InsureeGQLType)


schema = graphene.Schema(query=Query)
