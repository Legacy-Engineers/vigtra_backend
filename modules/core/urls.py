from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .module_loader import get_module_urls
from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie
from django.conf import settings

urlpatterns = [
    path(
        "graphql/",
        csrf_exempt(jwt_cookie(GraphQLView.as_view(graphiql=settings.DEBUG))),
    ),
]

urlpatterns.extend(get_module_urls())
