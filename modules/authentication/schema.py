import graphene
from modules.authentication.gql import gql_queries, gql_mutations
from graphene_django.filter import DjangoFilterConnectionField
import graphql_jwt


class Query(graphene.ObjectType):
    permissions = DjangoFilterConnectionField(gql_queries.PermissionGQLType)
    user_groups = DjangoFilterConnectionField(gql_queries.GroupGQLType)
    users = DjangoFilterConnectionField(gql_queries.UserGQLType)
    user_info = graphene.Field(gql_queries.UserGQLType)

    def resolve_user_info(self, info, **kwargs):
        print(info.context.user)
        return None


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_user = gql_mutations.CreateUserMutation.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
