from django.db import models
from modules.medical.models.item import Item
from modules.medical.models.service import Service
from modules.core.models.abstract_models import UUIDModel
from django.utils import timezone


class ServiceItemStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"
    DRAFT = "draft", "Draft"


class ServiceItem(UUIDModel):
    parent = models.ForeignKey(Service, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity_provided = models.IntegerField(blank=True, null=True)
    pcp_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    price_asked = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(
        max_length=20,
        choices=ServiceItemStatus.choices,
        default=ServiceItemStatus.ACTIVE,
    )

    class Meta:
        managed = True
        db_table = "tblServiceItems"


class ServiceContainedPackage(UUIDModel):
    service = models.ForeignKey(
        Service,
        on_delete=models.DO_NOTHING,
        db_column="ServiceId",
        related_name="servicesServices",
    )
    parent = models.ForeignKey(
        Service, on_delete=models.DO_NOTHING, db_column="ServiceLinked"
    )
    quantity_provided = models.IntegerField(blank=True, null=True)
    scp_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    price_asked = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(
        max_length=20,
        choices=ServiceItemStatus.choices,
        default=ServiceItemStatus.ACTIVE,
    )

    class Meta:
        managed = True
        db_table = "tblServiceContainedPackages"
