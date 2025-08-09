from graphene_django.filter import DjangoFilterConnectionField
from .gql import queries, mutations
import graphene


class Query(graphene.ObjectType):
    insurees = DjangoFilterConnectionField(queries.InsureeGQLType)


class Mutation(graphene.ObjectType):
    create_insuree = mutations.CreateInsureeMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
