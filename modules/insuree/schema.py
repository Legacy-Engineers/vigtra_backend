from graphene_django.filter import DjangoFilterConnectionField
from .gql import gql_queries, gql_mutations
from .models import Insuree
from .models.family import Family, FamilyMembership
from .utils import get_location_based_insurees
from modules.authentication.utils import check_user_gql_permission
import graphene


class Query(graphene.ObjectType):
    insurees = DjangoFilterConnectionField(gql_queries.InsureeGQLType)
    families = DjangoFilterConnectionField(gql_queries.FamilyGQLType)
    family_memberships = DjangoFilterConnectionField(
        gql_queries.FamilyMembershipGQLType, family_uuid=graphene.String(required=True)
    )
    insuree = graphene.Field(
        gql_queries.InsureeGQLType, uuid=graphene.String(required=True)
    )

    def resolve_insuree(self, info, uuid=None):
        user = info.context.user
        check_user_gql_permission(user)
        try:
            return Insuree.objects.get(uuid=uuid)
        except Insuree.DoesNotExist:
            return None

    def resolve_insurees(self, info, **kwargs):
        user = info.context.user
        query_set = None

        check_user_gql_permission(user)
        if user.is_superuser:
            query_set = Insuree.objects.all()
        elif user.has_perm("can_view_insuree"):
            if hasattr(user, "location"):
                query_set = get_location_based_insurees(user.location)
            elif hasattr(user, "health_facility"):
                pass

        return query_set

    def resolve_families(self, info, **kwargs):
        user = info.context.user
        check_user_gql_permission(user)

        if user.is_superuser or user.has_perm("can_view_family"):
            return Family.objects.all()
        return Family.objects.all()

    def resolve_family_memberships(self, info, family_uuid=None, **kwargs):
        user = info.context.user
        check_user_gql_permission(user)

        if user.is_superuser or user.has_perm("can_view_family_membership"):
            return FamilyMembership.objects.filter(family__uuid=family_uuid)

        return FamilyMembership.objects.none()


class Mutation(graphene.ObjectType):
    create_insuree = gql_mutations.CreateInsureeMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
