from django.db import models
from modules.core.models import abstract_models as core_models
from modules.authentication.models import User
from modules.contribution_plan.models import ContributionPlan
from django_lifecycle import LifecycleModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
from modules.location.models import Location
from modules.medical.models import Item, Service


class InsurancePlanStatus(models.IntegerChoices):
    IDLE = 1
    ACTIVE = 2
    SUSPENDED = 4
    EXPIRED = 8
    READY = 16


class InsurancePlanPeriodType(models.TextChoices):
    DAY = "D", "Day"
    WEEK = "W", "Week"
    MONTH = "M", "Month"
    YEAR = "Y", "Year"


class InsurancePlanStage(models.TextChoices):
    NEW = "N", "New"
    RENEWED = "R", "Renewed"
    CANCELLED = "C", "Cancelled"
    EXPIRED = "E", "Expired"
    SUSPENDED = "S", "Suspended"
    TERMINATED = "T", "Terminated"
    CLOSED = "X", "Closed"


class InsurancePlanScopeType(models.TextChoices):
    LOCATION_BASED = "L", "Location Based"
    MEMBER_BASED = "M", "Member Based"
    PRODUCT_BASED = "P", "Product Based"
    SERVICE_BASED = "S", "Service Based"
    OTHER = "O", "Other"


class InsurancePlan(core_models.VersionedModel, LifecycleModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
    code = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    stage = models.CharField(
        max_length=1, choices=InsurancePlanStage.choices, blank=True, null=True
    )
    status = models.SmallIntegerField(
        choices=InsurancePlanStatus.choices, blank=True, null=True
    )
    value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    # The one the policy is for
    policy_holder_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    policy_holder_id = models.TextField()
    policy_holder = GenericForeignKey("policy_holder_type", "policy_holder_id")

    officer = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    plan_scope_type = models.CharField(
        max_length=1, choices=InsurancePlanScopeType.choices, blank=True, null=True
    )

    threshold = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    max_members = models.IntegerField(blank=True, null=True)
    recurrence = models.PositiveIntegerField(blank=True, null=True)

    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    contribution_plan = models.ForeignKey(
        ContributionPlan,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    def is_new(self):
        return not self.stage or self.stage == InsurancePlan.STAGE_NEW

    class Meta:
        managed = True
        db_table = "tblInsurancePlans"


class InsurancePlanItem(core_models.VersionedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)

    insurance_plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    total_price = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )

    # The period of the item

    class Meta:
        managed = True
        db_table = "tblInsurancePlanItems"


class InsurancePlanService(core_models.VersionedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)

    insurance_plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    total_price = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = True
        db_table = "tblInsurancePlanServices"
