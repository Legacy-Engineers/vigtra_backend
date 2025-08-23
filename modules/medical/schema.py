from .gql import queries
import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.ObjectType):
    diagnoses = DjangoFilterConnectionField(queries.DiagnosisGQLType)
    services = DjangoFilterConnectionField(queries.ServiceGQLType)
    service_categories = DjangoFilterConnectionField(queries.ServiceCategoryGQLType)


schema = graphene.Schema(query=Query)
