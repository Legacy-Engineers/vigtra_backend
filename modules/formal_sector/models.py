from django.db import models
from modules.location.models import Location
from modules.insuree.models import Insuree
from modules.contribution_plan.models import ContributionPlanBundle

# Create your models here.

SECTOR_TYPE_CHOICES = [
    (1, "Private"),
    (2, "Public"),
    (3, "NGO"),
    (4, "Other"),
    (5, "International"),
    (6, "Cooperative"),
    (7, "Association"),
    (8, "Self Employed"),
    (9, "Informal"),
    (10, "Formal"),
    (11, "Other"),
]


class FormalSector(models.Model):
    code = models.CharField(db_column="FormalSectorCode", max_length=32)
    trade_name = models.CharField(db_column="TradeName", max_length=255)
    sector_type = models.CharField(max_length=10)
    sector_type_other = models.CharField(max_length=20, blank=True, null=True)
    location = models.ForeignKey(
        Location,
        db_column="LocationsId",
        on_delete=models.deletion.DO_NOTHING,
        blank=True,
        null=True,
    )
    address = models.JSONField(db_column="Address", blank=True, null=True)
    phone = models.CharField(db_column="Phone", max_length=16, blank=True, null=True)
    fax = models.CharField(db_column="Fax", max_length=16, blank=True, null=True)
    email = models.CharField(db_column="Email", max_length=255, blank=True, null=True)
    contact_name = models.JSONField(db_column="ContactName", blank=True, null=True)
    legal_form = models.IntegerField(db_column="LegalForm", blank=True, null=True)
    activity_code = models.IntegerField(db_column="ActivityCode", blank=True, null=True)
    accountancy_account = models.CharField(
        db_column="AccountancyAccount", max_length=64, blank=True, null=True
    )
    bank_account = models.JSONField(db_column="bankAccount", blank=True, null=True)
    payment_reference = models.CharField(
        db_column="PaymentReference", max_length=128, blank=True, null=True
    )

    class Meta:
        db_table = "tblFormalSector"


class FormalSectorInsuree(models.Model):
    formal_sector = models.ForeignKey(
        FormalSector, on_delete=models.deletion.DO_NOTHING
    )
    insuree = models.ForeignKey(
        Insuree, db_column="InsureeId", on_delete=models.deletion.DO_NOTHING
    )
    contribution_plan_bundle = models.ForeignKey(
        ContributionPlanBundle,
        db_column="ContributionPlanBundleId",
        on_delete=models.deletion.DO_NOTHING,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "tblFormalSectorInsuree"
