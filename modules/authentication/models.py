from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_("The username field must be set"))
        username = self.normalize_username(username)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    """
    Custom User model for the health software.
    """
    username = models.CharField(_("Username"), max_length=20, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = "tblUsers"
        permissions = [
            ("can_activate_user", "Can Activate user"),
            ("can_deactivate_user", "Can De-Activate user"),
            ("can_reset_user_password", "Can Reset User password user"),
        ]