import graphene
from .module_loader import get_module_queries, get_module_mutations
from .gql import gql_queries
from graphene_django.filter import DjangoFilterConnectionField

all_queries = get_module_queries()
all_mutations = get_module_mutations()


class Query(*all_queries, graphene.ObjectType):
    change_logs = DjangoFilterConnectionField(gql_queries.ChangeLogGQLType)


class Mutation(*all_mutations, graphene.ObjectType):
    pass


# Generate schema with or without Mutation
schema = graphene.Schema(query=Query, mutation=Mutation if all_mutations else None)
