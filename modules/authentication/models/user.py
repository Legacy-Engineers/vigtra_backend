from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from modules.location.models import Location, HealthFacility
from django.db.models.functions import Now
import uuid


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_("The username field must be set"))
        username = self.normalize_username(username)
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)

    def normalize_username(self, username):
        return username.lower()


class UserApplicationTypeChoices(models.TextChoices):
    REGULAR_USER = "REGULAR_USER", _("Regular User")
    LOCATION_BASED_USER = "LOCATION_BASED_USER", _("Location Based User")
    HEALTH_FACILITY_USER = "HEALTH_FACILITY_USER", _("Health Facility User")


class User(AbstractUser, PermissionsMixin):
    """
    Custom User model for the health software.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    username = models.CharField(_("Username"), max_length=20, unique=True)
    email = models.EmailField(_("email address"), unique=True)

    # Audit fields
    created_at = models.DateTimeField(
        _("created at"), default=timezone.now, db_default=Now()
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    user_application_type = models.CharField(
        max_length=255,
        choices=UserApplicationTypeChoices.choices,
        default=UserApplicationTypeChoices.REGULAR_USER,
        help_text=_("Type of user application"),
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Location of the user"),
    )

    health_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Health facility of the user"),
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "tblUsers"
        permissions = [
            ("can_activate_user", "Can Activate user"),
            ("can_deactivate_user", "Can De-Activate user"),
            ("can_reset_user_password", "Can Reset User password user"),
            ("can_view_insurees", "Can View Insurees"),
        ]
