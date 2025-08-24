from graphene_django.filter import DjangoFilterConnectionField
from modules.insurance_coverage.gql.queries import CoverageGQLType
import graphene


class Query(graphene.ObjectType):
    coverages = DjangoFilterConnectionField(CoverageGQLType)


schema = graphene.Schema(query=Query)
