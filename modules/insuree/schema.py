from graphene_django.filter import DjangoFilterConnectionField
from .gql import gql_queries, gql_mutations
from .models import Insuree
from .models.family import Family, FamilyMembership
from modules.authentication.models.user import UserApplicationTypeChoices
from modules.location.models import Location
import graphene
from django.db.models import QuerySet


def get_location_based_insurees(user_location: Location) -> QuerySet["Insuree"]:
    # This basically gets the location and all its descendants. MPTT is magic :).
    location_ids = user_location.get_descendants(include_self=True).values_list(
        "id", flat=True
    )

    # All the insurees within the location and its descendants. Easy peasy :).
    return Insuree.objects.filter(location_id__in=location_ids)


class Query(graphene.ObjectType):
    insurees = DjangoFilterConnectionField(gql_queries.InsureeGQLType)
    families = DjangoFilterConnectionField(gql_queries.FamilyGQLType)
    family_memberships = DjangoFilterConnectionField(
        gql_queries.FamilyMembershipGQLType
    )
    insuree = graphene.Field(gql_queries.InsureeGQLType, uuid=graphene.String())

    def resolve_insuree(self, info, uuid=None):
        try:
            return Insuree.objects.get(uuid=uuid)
        except Insuree.DoesNotExist:
            return None

    def resolve_insurees(self, info, **kwargs):
        user = info.context.user
        print(user)
        query_set = None
        if user.is_superuser:
            query_set = Insuree.objects.all()
        elif user.has_perm("can_view_insuree"):
            if (
                user.user_application_type
                == UserApplicationTypeChoices.LOCATION_BASED_USER
            ):
                if hasattr(user, "location"):
                    query_set = get_location_based_insurees(user.location)
                else:
                    raise Exception("User does not have a location")
        return query_set

    def resolve_families(self, info, **kwargs):
        user = info.context.user
        if user.is_superuser or user.has_perm("can_view_family"):
            return Family.objects.all()
        return Family.objects.all()

    def resolve_family_memberships(self, info, **kwargs):
        user = info.context.user
        if user.is_superuser or user.has_perm("can_view_family_membership"):
            return FamilyMembership.objects.all()
        return FamilyMembership.objects.none()


class Mutation(graphene.ObjectType):
    create_insuree = gql_mutations.CreateInsureeMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
