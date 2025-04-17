from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def _create_user(self):
        pass


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=True, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email
