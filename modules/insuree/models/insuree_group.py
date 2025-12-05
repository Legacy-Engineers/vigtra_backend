from django.db import models
from modules.core.models.abstract_models import UUIDModel, BaseCodeModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .insuree import Insuree


class InsureeGroupTypes(models.TextChoices):
    ANIMAL = "animal", "Animal"
    PRACTITIONER = "practitioner", "Practitioner"
    CARE_TEAM = "care-team", "Care Team"
    HEALTHCARE_SERVICE = "healthcare-service", "Healthcare Service"
    LOCATION = "location", "Location"
    ORGANIZATION = "organization", "Organization"
    RELATED_PERSON = "related-person", "Related Person"


class InsureeGroupMembershipType(models.TextChoices):
    DEFINITIONAL = "definitional", "Definitional"
    ENUMERATED = "enumerated", "Enumerated"


class InsureeGroup(UUIDModel, BaseCodeModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    managing_entity_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    managing_entity_object_id = models.TextField(blank=True, null=True)
    managin_entity = GenericForeignKey(
        "managing_entity_type", "managing_entity_object_id"
    )
    group_type = models.CharField(
        max_length=15,
        choices=InsureeGroupTypes.choices,
        default=InsureeGroupTypes.LOCATION,
    )

    class Meta:
        db_table = "tblInsureeGroup"


class InsureeGroupMembership(UUIDModel):
    group = models.ForeignKey(InsureeGroup, on_delete=models.CASCADE)
    insuree = models.ForeignKey(Insuree, on_delete=models.CASCADE)
    membership_type = models.CharField(
        max_length=15,
        choices=InsureeGroupMembershipType.choices,
        default=InsureeGroupMembershipType.DEFINITIONAL,
    )
    active = models.BooleanField(default=False)
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tblInsureeGroupMembership"
