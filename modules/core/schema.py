import graphene
from .module_loader import get_module_queries, get_module_mutations
from .gql import gql_queries
from graphene_django.filter import DjangoFilterConnectionField
from vigtra.extra_settings import ExtraSettings


def create_schema():
    """Create GraphQL schema with dynamic module loading."""

    extra_modules = ExtraSettings.get_extra_modules()
    # Get all module queries and mutations
    all_queries = get_module_queries()
    all_mutations = get_module_mutations()

    # Get all extra module queries and mutations
    all_queries.extend(extra_modules["app_schema_queries"])
    all_mutations.extend(extra_modules["app_schema_mutations"])

    class Query(*all_queries, graphene.ObjectType):
        """Main GraphQL Query with all module queries."""

        # Core queries
        change_logs = DjangoFilterConnectionField(
            gql_queries.ChangeLogGQLType, description="Query change logs with filtering"
        )
        crud_events = DjangoFilterConnectionField(
            gql_queries.CRUDEventGQLType, description="Query CRUD events with filtering"
        )
        login_events = DjangoFilterConnectionField(
            gql_queries.LoginEventGQLType,
            description="Query login events with filtering",
        )
        request_events = DjangoFilterConnectionField(
            gql_queries.RequestEventGQLType,
            description="Query request events with filtering",
        )

        # Health check
        health = graphene.String(description="API health check")

        def resolve_health(self, info):
            """Simple health check endpoint."""
            return "OK"

    # Only create Mutation class if there are mutations
    if all_mutations:

        class Mutation(*all_mutations, graphene.ObjectType):
            """Main GraphQL Mutation with all module mutations."""

            pass

        schema = graphene.Schema(query=Query, mutation=Mutation)
    else:
        schema = graphene.Schema(query=Query)

    return schema


# Create the schema
schema = create_schema()


# Optional: Add schema introspection helper
def get_schema_info():
    """Get basic information about the schema."""
    query_fields = list(schema.query._meta.fields.keys())
    mutation_fields = (
        list(schema.mutation._meta.fields.keys()) if schema.mutation else []
    )

    return {
        "query_fields": query_fields,
        "mutation_fields": mutation_fields,
        "total_queries": len(query_fields),
        "total_mutations": len(mutation_fields),
    }
