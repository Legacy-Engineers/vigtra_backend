import graphene
from .module_loader import get_module_queries, get_module_mutations


all_queries = tuple(get_module_queries())  # Tuple of base classes
all_mutations = tuple(get_module_mutations())

# Dynamically create the Query class
Query = type("Query", all_queries + (graphene.ObjectType,), {
    "hello": graphene.String(default_value="Hi!")
})

# Dynamically create the Mutation class (optional)
Mutation = type("Mutation", all_mutations + (graphene.ObjectType,), {}) if all_mutations else None

# Generate schema with or without Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
