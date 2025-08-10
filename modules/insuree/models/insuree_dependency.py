from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.core.models.openimis_core_models import BaseCodeModel
from modules.core.config_manager import ConfigManager


insuree_config = ConfigManager.get_insuree_config()

AGE_OF_MAJORITY = insuree_config.get(
    "max_age_of_majority", 18
)  # Defaulting the value to 18 incase the configuration was removed


class Gender(BaseCodeModel):
    """Gender lookup table with improved validation."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    GENDER_CHOICES = [
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (OTHER, _("Other")),
    ]

    code = models.CharField(
        db_column="Code",
        primary_key=True,
        max_length=1,
        choices=GENDER_CHOICES,
        help_text=_("Gender code"),
    )
    gender = models.CharField(
        db_column="Gender",
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Gender description"),
    )

    # Add indexes for better performance
    class Meta:
        managed = True
        db_table = "tblGenders"
        verbose_name = _("Gender")
        verbose_name_plural = _("Genders")
        indexes = [
            models.Index(fields=["code"], name="idx_gender_code"),
        ]


class Profession(models.Model):
    """Enhanced Profession model."""

    id = models.AutoField(db_column="ProfessionId", primary_key=True)
    profession = models.CharField(
        db_column="Profession",
        max_length=100,  # Increased length
        help_text=_("Profession name"),
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Profession code"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether profession is active")
    )

    class Meta:
        managed = True
        db_table = "tblProfessions"
        verbose_name = _("Profession")
        verbose_name_plural = _("Professions")
        ordering = ["profession"]
        indexes = [
            models.Index(fields=["profession"], name="idx_profession_name"),
            models.Index(fields=["is_active"], name="idx_profession_active"),
        ]

    def __str__(self):
        return self.profession


class Education(models.Model):
    """Enhanced Education model."""

    id = models.AutoField(db_column="EducationId", primary_key=True)
    education = models.CharField(
        db_column="Education",
        max_length=100,  # Increased length
        help_text=_("Education level"),
    )
    code = models.CharField(
        max_length=10, unique=True, blank=True, null=True, help_text=_("Education code")
    )
    level = models.PositiveSmallIntegerField(
        default=0, help_text=_("Education level rank")
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether education level is active")
    )

    class Meta:
        managed = True
        db_table = "tblEducations"
        verbose_name = _("Education")
        verbose_name_plural = _("Education Levels")
        ordering = ["level", "education"]
        indexes = [
            models.Index(fields=["education"], name="idx_education_name"),
            models.Index(fields=["level"], name="idx_education_level"),
            models.Index(fields=["is_active"], name="idx_education_active"),
        ]

    def __str__(self):
        return self.education


class IdentificationType(models.Model):
    """Enhanced Identification Type model."""

    code = models.CharField(
        primary_key=True,
        max_length=10,
        help_text=_("Identification type code"),
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Identification type name"),
    )
    regex = models.TextField(
        blank=True,
        null=True,
        help_text=_("Regular expression for validation"),
    )
    prefix = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Prefix for the identification code"),
    )
    suffix = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Suffix for the identification code"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether identification type is active")
    )

    class Meta:
        managed = True
        db_table = "tblIdentificationTypes"
        verbose_name = _("Identification Type")
        verbose_name_plural = _("Identification Types")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"], name="idx_id_type_code"),
            models.Index(fields=["is_active"], name="idx_id_type_active"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Relation(models.Model):
    """Enhanced Relation model."""

    id = models.AutoField(db_column="RelationId", primary_key=True)
    relation = models.CharField(
        db_column="Relation", max_length=50, help_text=_("Relationship description")
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Relationship code"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether relationship is active")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0, help_text=_("Sort order for display")
    )

    class Meta:
        managed = True
        db_table = "tblRelations"
        verbose_name = _("Relation")
        verbose_name_plural = _("Relations")
        ordering = ["sort_order", "relation"]
        indexes = [
            models.Index(fields=["relation"], name="idx_relation_name"),
            models.Index(fields=["is_active"], name="idx_relation_active"),
        ]

    def __str__(self):
        return self.relation
