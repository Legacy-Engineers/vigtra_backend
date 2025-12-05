from django.db import models
from modules.core.models.abstract_models import UUIDModel
from modules.medical.utils import generate_medical_code
from simple_history.models import HistoricalRecords


class Diagnosis(UUIDModel):
    code = models.CharField(max_length=6, default=generate_medical_code)
    name = models.CharField(max_length=255)

    history = HistoricalRecords()

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        managed = True
        db_table = "tblDiagnosis"
