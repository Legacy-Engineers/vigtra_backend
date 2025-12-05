from django.db import models

from modules.core.models.abstract_models import BaseCodeModel, UUIDModel
from modules.insuree.models import Insuree, Family, Group


class EncounterStatusChoices(models.TextField):
    PLANNED = "planned", "Planned"
    IN_PROGRESS = "in-progress", "In Progress"
    ON_HOLD = "on-hold", "On Hold"
    DISCHARGED = "discharged", "Discharged"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    DISCONTINUED = "discontinued", "Discontinued"


class EncounterClassChoices(models.TextField):
    IN_PATIENT = "in-patient", "In Patient"
    OUT_PATIENT = "out-patient", "Out Patient"


class EncounterSubjectTypeChoices(models.TextChoices):
    INSUREE = "insuree", "Insuree"
    GROUP = "group", "Group"
    FAMILY = "family", "Family"


class Encounter(UUIDModel, BaseCodeModel):
    status = models.CharField(
        max_length=15,
        choices=EncounterStatusChoices.choices,
        default=EncounterStatusChoices.PLANNED,
    )
    classification = models.CharField(
        max_length=10,
        choices=EncounterClassChoices.choices,
        default=EncounterClassChoices.IN_PATIENT,
    )
    type = models.CharField(max_length=100)
    subject_type = models.CharField(
        max_length=100,
        choices=EncounterSubjectTypeChoices.choices,
        default=EncounterSubjectTypeChoices.INSUREE,
    )
    insuree = models.ForeignKey(Insuree, on_delete=models.CASCADE)

    class Meta(UUIDModel.Meta, BaseCodeModel.Meta):
        abstract = False
        db_table = "tblEncounter"
