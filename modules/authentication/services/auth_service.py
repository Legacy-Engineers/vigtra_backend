from typing import Dict
from modules.core.service_signals import register_signal
from modules.core.utils import vigtra_message
from ..models import User
import logging
import traceback

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user: User = None):
        self.user = user

    @register_signal("auth_service.create_or_update")
    def create_or_update(self, data: dict, **kwargs) -> Dict[str, bool | str | dict]:
        user_uuid = data.get("uuid")

        if user_uuid:
            return self.update(data=data)
        else:
            return self.create(data=data)

    @register_signal("auth_service.create_user")
    def create(self, data: dict, **kwargs) -> Dict[str, bool | str | dict]:
        try:
            validate_user = self._validate_new_user(data=data)
            if not validate_user.get("success"):
                return validate_user

            new_user = User.objects.create_user(**data)
            return vigtra_message(
                success=True,
                data=new_user.__dict__,
                message="User created successfully.",
            )
        except Exception as ex:
            tb_str = traceback.format_exc()
            return vigtra_message(
                data=data,
                message=f"Unexpected error: {ex}",
                error_details=[str(ex), tb_str],
            )

    def _validate_new_user(self, data: dict) -> Dict[str, bool | str | dict]:
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if not data.get(field):
                return vigtra_message(success=False, message=f"{field} is required.")

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return vigtra_message(
                success=False, message="Username, Email, and Password must be provided."
            )

        if User.objects.filter(username=username).exists():
            return vigtra_message(success=False, message="Username already exists.")

        if User.objects.filter(email=email).exists():
            return vigtra_message(success=False, message="Email already exists.")

        if len(password) < 8:
            return vigtra_message(
                success=False, message="Password must be at least 8 characters long."
            )

        if not any(char.isdigit() for char in password):
            return vigtra_message(
                success=False, message="Password must contain at least one digit."
            )

        if not any(char.isalpha() for char in password):
            return vigtra_message(
                success=False, message="Password must contain at least one letter."
            )

        if not any(char.isupper() for char in password):
            return vigtra_message(
                success=False,
                message="Password must contain at least one uppercase letter.",
            )

        if not any(char.isdigit() for char in password):
            return vigtra_message(
                success=False, message="Password must contain at least one digit."
            )

        if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password):
            return vigtra_message(
                success=False,
                message="Password must contain at least one special character.",
            )

        return vigtra_message(
            success=True,
            message="Validation successful.",
        )

    @register_signal("auth_service.update_user")
    def update(self, data: dict, **kwargs) -> Dict[str, bool | str | dict]:
        try:
            current_user = User.objects.get(uuid=data.get("uuid"))
            for key, value in data.items():
                if hasattr(current_user, key):
                    setattr(current_user, key, value)
            current_user.save()
            return vigtra_message(
                success=True,
                data=current_user.__dict__,
                message="User updated successfully.",
            )
        except User.DoesNotExist:
            logger.error(f"User not found: {data}")
            return vigtra_message(
                data=data,
                message="User not found.",
                error_details=[traceback.format_exc()],
            )
        except ValueError as va:
            logger.error(f"Value error: {va}")
            return vigtra_message(
                data=data,
                message=f"Value error: {va}",
                error_details=[str(va), traceback.format_exc()],
            )
        except Exception as ex:
            logger.error(f"An unexpected error: {ex}")
            return vigtra_message(
                data=data,
                message=f"An unexpected error: {ex}",
                error_details=[str(ex), traceback.format_exc()],
            )
