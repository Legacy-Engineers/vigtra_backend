from .gql import gql_queries
from graphene_django.filter import DjangoFilterConnectionField
import graphene


class Query(graphene.ObjectType):
    insurance_plans = DjangoFilterConnectionField(gql_queries.InsurancePlanGQLType)


schema = graphene.Schema(query=Query)
