from modules.location.gql import gql_queries, gql_mutations
import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.ObjectType):
    locations = DjangoFilterConnectionField(gql_queries.LocationGQLType)
    health_facilities = DjangoFilterConnectionField(gql_queries.HealthFacilityGQLType)
    location_types = DjangoFilterConnectionField(gql_queries.LocationTypeGQLType)


schema = graphene.Schema(query=Query)
