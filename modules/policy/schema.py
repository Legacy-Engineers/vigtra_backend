from .gql import gql_queries
from graphene_django.filter import DjangoFilterConnectionField
import graphene


class Query(graphene):
    policys = DjangoFilterConnectionField(gql_queries.PolicyGQLType)


schema = graphene.Schema(query=Query)
