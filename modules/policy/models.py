from django.db import models
from modules.core.models import openimis_core_models as core_models
from modules.authentication.models import User
from modules.product.models import Product
from modules.contribution_plan.models import ContributionPlan
from django_lifecycle import LifecycleModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid


class PolicyStatus(models.IntegerChoices):
    IDLE = 1
    ACTIVE = 2
    SUSPENDED = 4
    EXPIRED = 8
    READY = 16


class PolicyStage(models.TextChoices):
    NEW = "N", "New"
    RENEWED = "R", "Renewed"
    CANCELLED = "C", "Cancelled"
    EXPIRED = "E", "Expired"
    SUSPENDED = "S", "Suspended"
    TERMINATED = "T", "Terminated"
    CLOSED = "X", "Closed"


class Policy(core_models.VersionedModel, LifecycleModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)

    stage = models.CharField(
        max_length=1, choices=PolicyStage.choices, blank=True, null=True
    )
    status = models.SmallIntegerField(
        choices=PolicyStatus.choices, blank=True, null=True
    )
    value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    # The one the policy is for
    policy_holder_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    policy_holder_id = models.TextField()
    policy_holder = GenericForeignKey("policy_holder_type", "policy_holder_id")

    enroll_date = models.DateField()
    start_date = models.DateField()
    effective_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    product = models.ForeignKey(Product, models.DO_NOTHING)
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
    creation_date = models.DateField(auto_now=True, blank=True, null=True)
    updation_date = models.DateField(auto_now_add=True, blank=True, null=True)

    def claim_ded_rems(self):
        return self.claim_ded_rems

    def is_new(self):
        return not self.stage or self.stage == Policy.STAGE_NEW

    class Meta:
        managed = True
        db_table = "tblPolicies"
