import graphene
from modules.authentication.gql import gql_queries, gql_mutations
from graphene_django import DjangoConnectionField

class Query(graphene.ObjectType):
    permissions =DjangoConnectionField(gql_queries.PermissionGQLType)
    user_groups =DjangoConnectionField(gql_queries.GroupGQLType)



schema = graphene.Schema(query=Query)