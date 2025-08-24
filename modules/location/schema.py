from modules.location.gql import gql_queries, gql_mutations
import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.ObjectType):
    locations = DjangoFilterConnectionField(gql_queries.LocationGQLType)
    health_facilities = DjangoFilterConnectionField(gql_queries.HealthFacilityGQLType)
    location_types = DjangoFilterConnectionField(gql_queries.LocationTypeGQLType)
    health_facility_types = DjangoFilterConnectionField(
        gql_queries.HealthFacilityTypeGQLType
    )


class Mutation(graphene.ObjectType):
    # Location Type mutations
    create_location_type = gql_mutations.CreateLocationTypeMutation.Field()
    update_location_type = gql_mutations.UpdateLocationTypeMutation.Field()
    delete_location_type = gql_mutations.DeleteLocationTypeMutation.Field()

    # Location mutations
    create_location = gql_mutations.CreateLocationMutation.Field()
    update_location = gql_mutations.UpdateLocationMutation.Field()
    delete_location = gql_mutations.DeleteLocationMutation.Field()

    # Health Facility Type mutations
    create_health_facility_type = gql_mutations.CreateHealthFacilityTypeMutation.Field()
    update_health_facility_type = gql_mutations.UpdateHealthFacilityTypeMutation.Field()
    delete_health_facility_type = gql_mutations.DeleteHealthFacilityTypeMutation.Field()

    # Health Facility mutations
    create_health_facility = gql_mutations.CreateHealthFacilityMutation.Field()
    update_health_facility = gql_mutations.UpdateHealthFacilityMutation.Field()
    delete_health_facility = gql_mutations.DeleteHealthFacilityMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
