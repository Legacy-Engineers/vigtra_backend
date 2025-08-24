from graphene_django import DjangoObjectType
from modules.core.utils import prefix_filterset
import graphene


class InsureeGQLType(DjangoObjectType):
    class Meta:
        model = None  # Will be set dynamically
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "chf_id": ["exact", "icontains", "istartswith"],
            "last_name": ["exact", "icontains", "istartswith"],
            "other_names": ["exact", "icontains", "istartswith"],
            "dob": ["exact", "gte", "lte"],
            "marital_status": ["exact"],
            "passport": ["exact", "icontains"],
            "status": ["exact"],
            "offline": ["exact"],
            "created_date": ["exact", "gte", "lte"],
            "last_modified": ["exact", "gte", "lte"],
            "location__name": ["exact", "icontains"],
            "location__code": ["exact", "icontains"],
            "health_facility__name": ["exact", "icontains"],
            "health_facility__code": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    age = graphene.Int(description="Calculated age based on date of birth")
    full_name = graphene.String(description="Full name (last_name + other_names)")
    is_adult = graphene.Boolean(description="Whether the insuree is an adult")
    current_family_name = graphene.String(description="Name of current family")
    is_head_of_family = graphene.Boolean(
        description="Whether the insuree is head of family"
    )

    def resolve_age(self, info):
        if self.dob:
            from datetime import date

            today = date.today()
            return (
                today.year
                - self.dob.year
                - ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
        return None

    def resolve_full_name(self, info):
        return f"{self.last_name} {self.other_names}".strip()

    def resolve_is_adult(self, info):
        if self.dob:
            from datetime import date
            from modules.insuree.models.insuree_dependency import AGE_OF_MAJORITY

            today = date.today()
            age = (
                today.year
                - self.dob.year
                - ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
            return age >= AGE_OF_MAJORITY
        return None

    def resolve_current_family_name(self, info):
        current_family = getattr(self, "current_family", None)
        return current_family.name if current_family else None

    def resolve_is_head_of_family(self, info):
        return getattr(self, "is_head_of_family", False)


class FamilyGQLType(DjangoObjectType):
    class Meta:
        model = None  # Will be set dynamically
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "is_active": ["exact"],
            "created_date": ["exact", "gte", "lte"],
            "last_modified": ["exact", "gte", "lte"],
            "location__name": ["exact", "icontains"],
            "location__code": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    member_count = graphene.Int(description="Number of active family members")
    head_member = graphene.Field(InsureeGQLType, description="Head of family member")
    active_members = graphene.List(
        InsureeGQLType, description="List of active family members"
    )

    def resolve_member_count(self, info):
        return getattr(self, "member_count", 0)

    def resolve_head_member(self, info):
        return getattr(self, "head_member", None)

    def resolve_active_members(self, info):
        return getattr(self, "active_members", [])


class FamilyMembershipGQLType(DjangoObjectType):
    class Meta:
        model = None  # Will be set dynamically
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "is_head": ["exact"],
            "status": ["exact"],
            "membership_start_date": ["exact", "gte", "lte"],
            "membership_end_date": ["exact", "gte", "lte"],
            "family__name": ["exact", "icontains"],
            "insuree__chf_id": ["exact", "icontains"],
            "insuree__last_name": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)

    # Custom fields
    insuree_full_name = graphene.String(description="Full name of the insuree")
    family_name = graphene.String(description="Name of the family")
    relationship_name = graphene.String(description="Name of the relationship")

    def resolve_insuree_full_name(self, info):
        if self.insuree:
            return f"{self.insuree.last_name} {self.insuree.other_names}".strip()
        return None

    def resolve_family_name(self, info):
        return self.family.name if self.family else None

    def resolve_relationship_name(self, info):
        return self.relationship.name if self.relationship else None


# Set the models dynamically after Django is ready
def _set_insuree_models():
    from modules.insuree.models.insuree import Insuree
    from modules.insuree.models.family import Family, FamilyMembership
    InsureeGQLType._meta.model = Insuree
    FamilyGQLType._meta.model = Family
    FamilyMembershipGQLType._meta.model = FamilyMembership


# This will be called when Django is ready
try:
    from django.apps import apps
    if apps.is_installed('modules.insuree'):
        _set_insuree_models()
except:
    pass
