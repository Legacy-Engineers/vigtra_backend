from graphene_django.filter import DjangoFilterConnectionField
from modules.formal_sector.gql.gql_queries import (
    FormalSectorGQLType,
    FormalSectorInsureeGQLType,
)
import graphene


class Query(graphene.ObjectType):
    formal_sectors = DjangoFilterConnectionField(FormalSectorGQLType)
    formal_sector_insurees = DjangoFilterConnectionField(FormalSectorInsureeGQLType)


schema = graphene.Schema(query=Query)
