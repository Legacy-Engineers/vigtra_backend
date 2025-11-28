from django.contrib.auth.models import AnonymousUser, PermissionDenied
import graphene

from modules.insuree.models import Insuree


class InsureeDAshboardMetricGQLType(graphene.ObjectType):
    total_count = graphene.Int()


class DashboardMetricGQLType(graphene.ObjectType):
    insuree = graphene.Field(InsureeDAshboardMetricGQLType)

    def resolve_insuree(self, info):
        user = info.context.user

        if isinstance(user, AnonymousUser):
            raise PermissionDenied("You don't have permission to access this resource")
        insuree = Insuree.objects.all()
