from django.contrib.auth import PermissionDenied
from django.contrib.auth.models import AnonymousUser


def check_user_gql_permission(user):
    if isinstance(user, AnonymousUser):
        raise PermissionDenied("You don't have permission to this resource")
