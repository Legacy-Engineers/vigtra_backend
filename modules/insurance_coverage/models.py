from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from modules.core.models import openimis_core_models as core_models
from modules.insurance_plan.models import InsurancePlan
import uuid


class Coverage(core_models.VersionedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)

    insurance_plan = models.ForeignKey(
        InsurancePlan,
        on_delete=models.PROTECT,
        related_name="coverages",
    )

    # Policy holder (generic FK) - can be insuree, family, org, etc.
    policy_holder_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    policy_holder_id = models.TextField()
    policy_holder = GenericForeignKey("policy_holder_type", "policy_holder_id")

    # Payor (could be same as policy_holder or different: Org, Patient, etc.)
    payor_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="coverage_payor_type"
    )
    payor_id = models.TextField()
    payor = GenericForeignKey("payor_type", "payor_id")

    status = models.CharField(max_length=30, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "tblCoverage"

    def __str__(self):
        return f"Coverage for {self.policy_holder} under {self.insurance_plan}"
