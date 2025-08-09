from django.db import models
from modules.core.models.openimis_core_models import UUIDModel


class CareType(UUIDModel):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        managed = True
        db_table = "tblMedicalCareTypes"


class MedicalPackage(UUIDModel):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        managed = True
        db_table = "tblMedicalPackages"


class PatientCategory(UUIDModel):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        managed = True
        db_table = "tblPatientCategories"
