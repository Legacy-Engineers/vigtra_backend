from django.urls import path
from .module_loader import get_module_urls
from graphene_django.views import GraphQLView


urlpatterns = [
    path("graphql/", GraphQLView.as_view(graphiql=True)),
]

urlpatterns.extend(get_module_urls())