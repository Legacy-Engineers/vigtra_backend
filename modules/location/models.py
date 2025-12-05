from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey
from guardian.models import BaseObjectPermission

from modules.core.models.abstract_models import UUIDModel
from simple_history.models import HistoricalRecords
from django.utils import timezone


class LocationType(models.Model):
    """
    Defines hierarchical location types (e.g., Country, State, City, District).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Location Type Name",
        help_text="Name of the location type (e.g., Country, State, City)",
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Hierarchy Level",
        validators=[MinValueValidator(1)],
        help_text="Hierarchy level (1 for highest level, increasing for lower levels)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tblLocationTypes"
        verbose_name = "Location Type"
        verbose_name_plural = "Location Types"
        ordering = ["level", "name"]
        constraints = [
            models.UniqueConstraint(fields=["level"], name="unique_location_type_level")
        ]

    def __str__(self):
        return f"{self.name} (Level {self.level})"

    def clean(self):
        """Validate that level is positive."""
        if self.level and self.level < 1:
            raise ValidationError("Level must be at least 1.")


class Location(MPTTModel):
    """
    Hierarchical location model using MPTT for efficient tree operations.
    """

    name = models.CharField(
        max_length=100, verbose_name="Location Name", help_text="Name of the location"
    )
    type = models.ForeignKey(
        LocationType,
        on_delete=models.PROTECT,
        verbose_name="Location Type",
        help_text="Type of this location",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Location",
        help_text="Parent location in the hierarchy",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Location Code",
        help_text="Optional unique code for the location",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this location is currently active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tblLocations"
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["tree_id", "lft"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "parent"], name="unique_location_name_per_parent"
            )
        ]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self, separator=" > "):
        """Return the full hierarchical path of the location."""
        ancestors = self.get_ancestors(include_self=True)
        return separator.join(ancestor.name for ancestor in ancestors)

    def clean(self):
        """Validate location hierarchy constraints."""
        if self.parent and self.type:
            # Ensure parent's type level is lower than current type level
            if self.parent.type.level >= self.type.level:
                raise ValidationError(
                    f"Parent location type level ({self.parent.type.level}) "
                    f"must be lower than current type level ({self.type.level})"
                )

    @property
    def child_count(self):
        """Return the number of direct children."""
        return self.children.filter(is_active=True).count()

    @property
    def descendant_count(self):
        """Return the total number of descendants."""
        return self.get_descendants().filter(is_active=True).count()


class HealthFacilityQualityAssuranceChoices(models.TextChoices):
    """
    Choices for health facility quality assurance status.
    """

    ACCREDITED = "accredited", "Accredited"
    NON_ACCREDITED = "non_accredited", "Non-Accredited"
    IN_PROGRESS = "in_progress", "In Progress"


class HealthFacilityType(models.Model):
    """
    Defines types of health facilities (e.g., Hospital, Clinic, Health Center).
    """

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Facility Type Name"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tblHealthFacilityTypes"
        verbose_name = "Health Facility Type"
        verbose_name_plural = "Health Facility Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class HealthFacility(UUIDModel):
    """
    Represents a health facility with its location and operational details.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Facility Code",
        help_text="Unique identifier code for the facility",
    )
    name = models.CharField(
        max_length=200,  # Increased length for longer facility names
        verbose_name="Facility Name",
        help_text="Official name of the health facility",
    )
    facility_type = models.ForeignKey(
        HealthFacilityType,
        on_delete=models.PROTECT,
        verbose_name="Facility Type",
        help_text="Type of health facility",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Facility Description",
        help_text="Additional details about the facility",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,  # Changed from DO_NOTHING to PROTECT
        verbose_name="Facility Location",
        help_text="Geographic location of the facility",
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name="Physical Address",
        help_text="Street address and other location details",
    )
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Phone Number"
    )
    email = models.EmailField(null=True, blank=True, verbose_name="Email Address")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this facility is currently operational",
    )
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Established Date",
        help_text="Date when the facility was established",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    validity_from = models.DateTimeField(db_column="ValidityFrom", default=timezone.now)
    validity_to = models.DateTimeField(db_column="ValidityTo", blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "tblHealthFacilities"
        verbose_name = "Health Facility"
        verbose_name_plural = "Health Facilities"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "location"], name="unique_facility_name_per_location"
            )
        ]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["location"]),
            models.Index(fields=["facility_type"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate facility data."""
        if self.code:
            self.code = self.code.upper().strip()

        if self.name:
            self.name = self.name.strip()

    @property
    def full_address(self):
        """Return the complete address including location hierarchy."""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.location:
            parts.append(self.location.get_full_path())
        return ", ".join(parts)

    @property
    def display_name(self):
        """Return a display-friendly name with location."""
        if self.location:
            return f"{self.name} - {self.location.name}"
        return self.name


class LocationObjectLevelPermissionBase(BaseObjectPermission):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        abstract = True
