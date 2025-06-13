from graphene_django.filter import DjangoFilterConnectionField
from .gql import gql_queries, gql_mutations
import graphene


class Query(graphene.ObjectType):
    insurees = DjangoFilterConnectionField(gql_queries.InsureeGQLType)


class Mutation(graphene.ObjectType):
    create_insuree = gql_mutations.CreateInsureeMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
