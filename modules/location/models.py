from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class LocationType(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Location Type Name"
    )
    level = models.PositiveSmallIntegerField(verbose_name="Hierarchy Level")

    class Meta:
        db_table = "tblLocationTypes"
        verbose_name = "Location Type"
        verbose_name_plural = "Location Types"
        ordering = ["level"]

    def __str__(self):
        return self.name


class Location(MPTTModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Location Name")
    type = models.ForeignKey(
        LocationType, on_delete=models.DO_NOTHING, verbose_name="Location Type"
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Location",
    )

    class Meta:
        db_table = "tblLocations"
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["tree_id", "lft"]

    def __str__(self):
        return self.name


class HealthFacility(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Facility Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Facility Name")
    description = models.TextField(
        null=True, blank=True, verbose_name="Facility Description"
    )
    location = models.ForeignKey(
        Location, on_delete=models.DO_NOTHING, verbose_name="Facility Location"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        db_table = "tblHealthFacilities"
        verbose_name = "Health Facility"
        verbose_name_plural = "Health Facilities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"
