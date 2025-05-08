from django.db import models
from modules.openimis_modules.openimis_core import models as core_models
from modules.authentication.models import User
from modules.openimis_modules.product.models import Product
from modules.openimis_modules.contribution.models import ContributionPlan

import uuid

STATUS_CHOICES = [
    (1, "IDLE"),
    (2, "ACTIVE"),
    (4, "SUSPENDED"),
    (8, "EXPIRED"),
    (16, "READY"),
]


STAGE_CHOICES = [
    ("N", "New"),
    ("R", "Renewed"),
    ("C", "Cancelled"),
    ("E", "Expired"),
    ("S", "Suspended"),
    ("T", "Terminated"),
    ("X", "Closed"),
]

POLICY_HOLDER_TYPE_CHOICES = [
    (1, "Insuree"),
    (2, "Family"),
    (3, "Employer"),
    (4, "Group/Organization"),
    (5, "Institution"),
]

class Policy(core_models.VersionedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(
        max_length=36, default=uuid.uuid4, unique=True
    )

    stage = models.CharField(
        max_length=1, blank=True, null=True, choices=STAGE_CHOICES
    )
    status = models.SmallIntegerField( blank=True, null=True)
    value = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    policy_holder_id = models.CharField(max_length=100)
    policy_holder_type = models.CharField(max_length=2, )

    enroll_date = models.DateField()
    start_date = models.DateField()
    effective_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    product = models.ForeignKey(
        Product, models.DO_NOTHING
    )
    officer = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    offline = models.BooleanField(blank=True, null=True)
    audit_user_id = models.IntegerField()
    contribution_plan = models.ForeignKey(
        ContributionPlan,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    creation_date = models.DateField(
        auto_now=True, blank=True, null=True
    )

    def claim_ded_rems(self):
        return self.claim_ded_rems

    def is_new(self):
        return not self.stage or self.stage == Policy.STAGE_NEW

    class Meta:
        managed = True
        db_table = "tblPolicies"