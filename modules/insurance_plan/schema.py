from modules.insurance_plan.gql import gql_queries, gql_mutations
import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.ObjectType):
    insurance_plans = DjangoFilterConnectionField(gql_queries.InsurancePlanGQLType)
    insurance_plan_items = DjangoFilterConnectionField(
        gql_queries.InsurancePlanItemGQLType
    )
    insurance_plan_services = DjangoFilterConnectionField(
        gql_queries.InsurancePlanServiceGQLType
    )


class Mutation(graphene.ObjectType):
    # Insurance Plan mutations
    create_insurance_plan = gql_mutations.CreateInsurancePlanMutation.Field()
    update_insurance_plan = gql_mutations.UpdateInsurancePlanMutation.Field()
    delete_insurance_plan = gql_mutations.DeleteInsurancePlanMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
