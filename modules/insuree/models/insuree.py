from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
import uuid
from datetime import datetime, date
from modules.core.models import openimis_core_models as core_models
from modules.insuree.models.insuree_model_dependency import (
    Gender,
    Profession,
    Education,
    IdentificationType,
)
from .family import FamilyMembership

from modules.location import models as location_models
from .insuree_model_dependency import AGE_OF_MAJORITY
from django.conf import settings
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


class InsureeStatus(models.TextChoices):
    """Enhanced status choices with better naming."""

    ACTIVE = "AC", _("Active")
    INACTIVE = "IN", _("Inactive")
    DECEASED = "DE", _("Deceased")
    SUSPENDED = "SU", _("Suspended")
    PENDING = "PE", _("Pending")


class InsureeManager(models.Manager):
    """Custom manager for Insuree model."""

    def active(self):
        """Return only active insurees."""
        return self.filter(status=InsureeStatus.ACTIVE)

    def heads_of_family(self):
        """Return only heads of families."""
        from .family import FamilyMembershipStatus

        return self.filter(
            family_memberships__is_head=True,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
        ).distinct()

    def adults(self, reference_date=None):
        """Return only adult insurees."""
        if reference_date is None:
            reference_date = date.today()

        cutoff_date = reference_date - datetime.timedelta(days=AGE_OF_MAJORITY * 365.25)
        return self.filter(dob__lte=cutoff_date)

    def by_chf_id(self, chf_id):
        """Find insuree by CHF ID."""
        return self.filter(chf_id=chf_id)

    def in_family(self, family):
        """Return insurees in a specific family."""
        from .family import FamilyMembershipStatus

        return self.filter(
            family_memberships__family=family,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
        ).distinct()


class Insuree(
    core_models.VersionedModel,
    core_models.ExtendableModel,
    LifecycleModel,
):
    """Enhanced Insuree model with better validation and performance."""

    # Usage examples and migration helpers:
    """
    # Example usage of the new FamilyMembership model:

    # Create a family
    family = Family.objects.create(
        location=some_location,
        family_type=some_type,
        address="123 Main St",
        audit_user=user
    )

    # Create insurees
    head_insuree = Insuree.objects.create(
        chf_id="12345",
        last_name="Doe",
        other_names="John",
        # ... other fields
    )

    spouse_insuree = Insuree.objects.create(
        chf_id="12346",
        last_name="Doe",
        other_names="Jane",
        # ... other fields
    )

    # Add members to family using the new system
    head_membership = family.add_member(
        insuree=head_insuree,
        is_head=True,
        relationship=None  # Head has no relationship to themselves
    )

    spouse_membership = family.add_member(
        insuree=spouse_insuree,
        is_head=False,
        relationship=spouse_relation  # Relation object for spouse
    )

    # Transfer member to another family
    new_family = Family.objects.create(...)
    spouse_membership.transfer_to_family(new_family)

    # Get family members
    active_members = family.members  # Returns QuerySet of active members
    member_count = family.member_count
    adult_members = family.adult_members

    # Access family through insuree
    current_family = head_insuree.current_family
    is_head = head_insuree.is_head_of_family
    family_relationship = head_insuree.get_family_relationship()

    # Get family history for an insuree
    history = head_insuree.get_family_history()
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the insuree"),
    )

    chf_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_("CHF identification number"),
    )

    last_name = models.CharField(max_length=100, help_text=_("Last name"))

    other_names = models.CharField(max_length=100, help_text=_("Other names"))

    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Gender"),
    )

    dob = models.DateField(blank=True, null=True, help_text=_("Date of birth"))

    marital_status = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=[
            ("S", _("Single")),
            ("M", _("Married")),
            ("D", _("Divorced")),
            ("W", _("Widowed")),
        ],
        help_text=_("Marital status"),
    )

    # Enhanced validation for passport
    passport = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        help_text=_("Passport number"),
    )

    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Profession"),
    )

    education = models.ForeignKey(
        Education,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Education level"),
    )

    location = models.ForeignKey(
        location_models.Location,
        on_delete=models.CASCADE,
        help_text=_("Location of the insuree"),
    )

    health_facility = models.ForeignKey(
        location_models.HealthFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Associated health facility"),
    )

    secondary_health_facility = models.ForeignKey(
        location_models.HealthFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="insurees_secondary_health_facility",
        help_text=_("Secondary associated health facility"),
    )

    other_health_facilities = models.ManyToManyField(
        location_models.HealthFacility,
        related_name="insurees_other_health_facility",
        blank=True,
        help_text=_("Other associated health facility"),
    )

    offline = models.BooleanField(
        db_column="isOffline", default=False, help_text=_("Whether created offline")
    )

    status = models.CharField(
        max_length=2,
        choices=InsureeStatus.choices,
        default=InsureeStatus.ACTIVE,
        help_text=_("Current status"),
    )

    status_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date status was changed"),
    )

    # Additional useful fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date insuree was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date insuree was last modified")
    )

    notes = models.TextField(blank=True, null=True, help_text=_("Additional notes"))

    audit_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who last modified the insuree"),
    )

    objects = InsureeManager()

    def clean(self):
        """Enhanced validation for Insuree model."""
        super().clean()

        # Validate CHF ID uniqueness
        if self.chf_id:
            existing = Insuree.objects.filter(chf_id=self.chf_id).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"chf_id": _("CHF ID must be unique")})

        # Validate date of birth
        if self.dob and self.dob > date.today():
            raise ValidationError({"dob": _("Date of birth cannot be in the future")})

        # Validate identification number if type requires it
        if self.identification and self.identification.requires_validation:
            if not self.identification_number:
                raise ValidationError(
                    {
                        "identification_number": _(
                            "Identification number is required for this type"
                        )
                    }
                )

            if self.identification.validation_regex:
                import re

                if not re.match(
                    self.identification.validation_regex, self.identification_number
                ):
                    raise ValidationError(
                        {
                            "identification_number": _(
                                "Invalid identification number format"
                            )
                        }
                    )

    @hook(BEFORE_SAVE)
    def update_status_date(self):
        """Update status date when status changes."""
        if self.has_changed("status") and self.status:
            self.status_date = date.today()

    @hook(BEFORE_SAVE)
    def update_card_issued_date(self):
        """Update card issued date when card is issued."""
        if self.has_changed("card_issued") and self.card_issued:
            self.card_issued_date = date.today()

    @property
    def current_family(self):
        """Get current family through active membership."""
        from .family import FamilyMembershipStatus, FamilyMembership

        try:
            active_membership = self.family_memberships.get(
                status=FamilyMembershipStatus.ACTIVE
            )
            return active_membership.family
        except (
            FamilyMembership.DoesNotExist,
            FamilyMembership.MultipleObjectsReturned,
        ):
            return None

    @property
    def current_family_membership(self):
        """Get current family membership."""
        from .family import FamilyMembershipStatus, FamilyMembership

        try:
            return self.family_memberships.get(status=FamilyMembershipStatus.ACTIVE)
        except (
            FamilyMembership.DoesNotExist,
            FamilyMembership.MultipleObjectsReturned,
        ):
            return None

    @property
    def is_head_of_family(self):
        """Check if insuree is head of any family."""
        from .family import FamilyMembershipStatus

        return self.family_memberships.filter(
            is_head=True, status=FamilyMembershipStatus.ACTIVE
        ).exists()

    def get_family_relationship(self):
        """Get relationship to head of current family."""
        membership = self.current_family_membership
        return membership.relationship if membership else None

    def join_family(self, family, is_head=False, relationship=None, start_date=None):
        """Join a family."""
        return family.add_member(
            insuree=self,
            is_head=is_head,
            relationship=relationship,
            start_date=start_date,
        )

    def leave_family(self, end_date=None, reason=None):
        """Leave current family."""
        current_family = self.current_family
        if current_family:
            return current_family.remove_member(
                insuree=self, end_date=end_date, reason=reason
            )
        else:
            raise ValidationError(_("Insuree is not currently in any family"))

    def transfer_to_family(self, new_family, transfer_date=None):
        """Transfer to a new family."""
        current_membership = self.current_family_membership
        if current_membership:
            return current_membership.transfer_to_family(
                new_family=new_family, transfer_date=transfer_date
            )
        else:
            # If not in any family, just join the new one
            return self.join_family(new_family, start_date=transfer_date)

    def get_family_history(self):
        """Get complete family membership history."""
        return self.family_memberships.select_related(
            "family", "relationship"
        ).order_by("-membership_start_date")

    def age(self, reference_date=None):
        """Calculate age with better precision."""
        if not self.dob:
            return None

        if reference_date is None:
            reference_date = date.today()

        age = reference_date.year - self.dob.year
        if (reference_date.month, reference_date.day) < (self.dob.month, self.dob.day):
            age -= 1

        return max(0, age)  # Ensure age is not negative

    def is_adult(self, reference_date=None):
        """Check if insuree is adult."""
        age = self.age(reference_date)
        return age >= AGE_OF_MAJORITY if age is not None else None

    @property
    def full_name(self):
        """Return full name."""
        return f"{self.other_names} {self.last_name}".strip()

    @property
    def is_active(self):
        """Check if insuree is active."""
        return self.status == InsureeStatus.ACTIVE

    def __str__(self):
        return f"{self.chf_id or 'No CHF ID'} - {self.full_name}"

    phone = PhoneNumberField(blank=True, null=True, help_text=_("Phone number"))

    # Enhanced email validation
    email = models.EmailField(
        db_column="Email",
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Email address"),
    )

    current_address = models.CharField(
        db_column="CurrentAddress",
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Current address"),
    )

    geolocation = models.CharField(
        db_column="GeoLocation",
        max_length=250,
        blank=True,
        null=True,
        help_text=_("GPS coordinates"),
    )

    photo = models.ImageField(  # Changed to ImageField for better validation
        db_column="Photo",
        upload_to="insuree/photos/%Y/%m/",  # Better organization
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Photo of the insuree"),
    )

    photo_date = models.DateField(
        db_column="PhotoDate",
        blank=True,
        null=True,
        help_text=_("Date photo was taken"),
    )

    card_issued = models.BooleanField(
        db_column="CardIssued",
        default=False,
        help_text=_("Whether card has been issued"),
    )

    card_issued_date = models.DateField(
        blank=True, null=True, help_text=_("Date card was issued")
    )

    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Profession"),
    )

    education = models.ForeignKey(
        Education,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Education level"),
    )

    identification = models.ForeignKey(
        IdentificationType,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Identification type"),
    )

    identification_number = models.CharField(
        max_length=50, blank=True, null=True, help_text=_("Identification number")
    )

    health_facility = models.ForeignKey(
        location_models.HealthFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Associated health facility"),
    )

    offline = models.BooleanField(
        db_column="isOffline", default=False, help_text=_("Whether created offline")
    )

    status = models.CharField(
        max_length=2,
        choices=InsureeStatus.choices,
        default=InsureeStatus.ACTIVE,
        help_text=_("Current status"),
    )

    status_date = models.DateField(
        db_column="StatusDate",
        null=True,
        blank=True,
        help_text=_("Date status was changed"),
    )

    # Additional useful fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date insuree was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date insuree was last modified")
    )

    notes = models.TextField(blank=True, null=True, help_text=_("Additional notes"))

    audit_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the insuree"),
    )

    objects = InsureeManager()

    def clean(self):  # noqa: F811
        """Enhanced validation for Insuree model."""
        super().clean()

        # Validate CHF ID uniqueness
        if self.chf_id:
            existing = Insuree.objects.filter(chf_id=self.chf_id).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"chf_id": _("CHF ID must be unique")})

        # Validate date of birth
        if self.dob and self.dob > date.today():
            raise ValidationError({"dob": _("Date of birth cannot be in the future")})

        # Validate head of family
        if self.head and self.family:
            other_heads = self.family.members.filter(head=True).exclude(pk=self.pk)
            if other_heads.exists():
                raise ValidationError({"head": _("Family can only have one head")})

        # Validate identification number if type requires it
        if self.identification and self.identification.requires_validation:
            if not self.identification_number:
                raise ValidationError(
                    {
                        "identification_number": _(
                            "Identification number is required for this type"
                        )
                    }
                )

            if self.identification.validation_regex:
                import re

                if not re.match(
                    self.identification.validation_regex, self.identification_number
                ):
                    raise ValidationError(
                        {
                            "identification_number": _(
                                "Invalid identification number format"
                            )
                        }
                    )

    @hook(BEFORE_SAVE)
    def update_status_date(self):  # noqa: F811
        """Update status date when status changes."""
        if self.has_changed("status") and self.status:
            self.status_date = date.today()

    @hook(BEFORE_SAVE)
    def update_card_issued_date(self):  # noqa: F811
        """Update card issued date when card is issued."""
        if self.has_changed("card_issued") and self.card_issued:
            self.card_issued_date = date.today()

    def is_head_of_family(self):  # noqa: F811
        """Check if insuree is head of family."""
        fam_membership = FamilyMembership.objects.filter(insuree=self)

        if fam_membership:
            if fam_membership.is_head:
                return True

        return False

    def age(self, reference_date=None):  # noqa: F811
        """Calculate age with better precision."""
        if not self.dob:
            return None

        if reference_date is None:
            reference_date = date.today()

        age = reference_date.year - self.dob.year
        if (reference_date.month, reference_date.day) < (self.dob.month, self.dob.day):
            age -= 1

        return max(0, age)  # Ensure age is not negative

    def is_adult(self, reference_date=None):  # noqa: F811
        """Check if insuree is adult."""
        age = self.age(reference_date)
        return age >= AGE_OF_MAJORITY if age is not None else None

    @property
    def full_name(self):  # noqa: F811
        """Return full name."""
        return f"{self.other_names} {self.last_name}".strip()

    @property
    def is_active(self):  # noqa: F811
        """Check if insuree is active."""
        return self.status == InsureeStatus.ACTIVE

    def __str__(self):  # noqa: F811
        return f"{self.chf_id or 'No CHF ID'} - {self.full_name}"

    class Meta:  # noqa: F811
        managed = True
        db_table = "tblInsurees"
        verbose_name = _("Insuree")
        verbose_name_plural = _("Insurees")
        indexes = [
            models.Index(fields=["chf_id"], name="idx_insuree_chfid"),
            models.Index(fields=["last_name", "other_names"], name="idx_insuree_names"),
            models.Index(fields=["dob"], name="idx_insuree_dob"),
            models.Index(fields=["status"], name="idx_insuree_status"),
            models.Index(fields=["gender"], name="idx_insuree_gender"),
            models.Index(fields=["created_date"], name="idx_insuree_created"),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_insuree_validity"
            ),
            models.Index(
                fields=["identification_number"], name="idx_insuree_id_number"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["chf_id"],
                condition=Q(chf_id__isnull=False),
                name="unique_chf_id",
            ),
            # Note: Date of birth validation is handled in the clean() method
            # to avoid issues with datetime.date.today() at class definition time
        ]


class InsureeIdentification(models.Model):
    """Model for insuree identification."""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        null=True,
        blank=True,
        help_text=_("Unique identifier for the insuree identification"),
    )
    insuree = models.ForeignKey(Insuree, on_delete=models.CASCADE, help_text=_("Insuree"))
    identification_type = models.ForeignKey(IdentificationType, on_delete=models.CASCADE, help_text=_("Identification type"))
    identification_number = models.CharField(max_length=50, help_text=_("Identification number"))

    class Meta:
        managed = True
        db_table = "tblInsureeIdentifications"
        verbose_name = _("Insuree Identification")
        verbose_name_plural = _("Insuree Identifications")