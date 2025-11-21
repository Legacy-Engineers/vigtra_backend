from modules.core.config_manager import ConfigManager
import re
import string
import random
import logging
from .models import Insuree
from modules.location.models import Location

logger = logging.getLogger(__name__)

insuree_config = ConfigManager.get_insuree_config()


class CHFIDGenerationError(Exception):
    """Custom exception for CHF ID generation failures."""

    pass


def validate_chf_config(chf_config):
    """
    Validate CHF configuration for compatibility.

    Args:
        chf_config (dict): CHF configuration dictionary

    Raises:
        CHFIDGenerationError: If configuration is invalid
    """
    prefix = chf_config.get("prefix", "CHF")
    regex = chf_config.get("regex", None)
    length = chf_config.get("length", 10)

    # Validate length
    if not isinstance(length, int) or length < 1:
        raise CHFIDGenerationError(
            f"Invalid length configuration: {length}. Must be a positive integer."
        )

    # Validate prefix
    if not isinstance(prefix, str):
        raise CHFIDGenerationError(
            f"Invalid prefix configuration: {prefix}. Must be a string."
        )

    # Validate regex if provided
    if regex:
        try:
            re.compile(regex)
        except re.error as e:
            raise CHFIDGenerationError(f"Invalid regex pattern: {regex}. Error: {e}")

        # Check if the regex is potentially compatible with the prefix
        test_id = f"{prefix}{'a' * length}"
        if not re.match(regex, test_id):
            logger.warning(
                f"Regex pattern '{regex}' may not be compatible with prefix '{prefix}' "
                f"and length {length}. Consider adjusting the configuration."
            )


def generate_random_alphanumeric(length):
    """
    Generate a random alphanumeric string of specified length.
    Uses a mix of uppercase, lowercase letters and digits for better regex compatibility.

    Args:
        length (int): Length of the random string

    Returns:
        str: Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_insuree_chf_id(max_attempts=100):
    """
    Generate a CHF ID according to configuration with proper error handling.

    Args:
        max_attempts (int): Maximum number of generation attempts before giving up

    Returns:
        str: Generated CHF ID

    Raises:
        CHFIDGenerationError: If unable to generate a valid CHF ID
    """
    try:
        chf_config = insuree_config.get("chf_config", {})

        # Validate configuration
        validate_chf_config(chf_config)

        prefix = chf_config.get("prefix", "CHF")
        regex = chf_config.get("regex", None)
        length = chf_config.get("length", 10)

        logger.debug(
            f"Generating CHF ID with config: prefix='{prefix}', length={length}, regex='{regex}'"
        )

        for attempt in range(max_attempts):
            # Use alphanumeric generation for better regex compatibility
            random_id = generate_random_alphanumeric(length)
            generated_chf_id = f"{prefix}{random_id}"

            # If no regex is specified, return the generated ID
            if not regex:
                logger.debug(
                    f"Generated CHF ID: {generated_chf_id} (no regex validation)"
                )
                return generated_chf_id

            # Validate against regex
            if re.match(regex, generated_chf_id):
                logger.debug(
                    f"Generated valid CHF ID: {generated_chf_id} (attempt {attempt + 1})"
                )
                return generated_chf_id
            else:
                logger.debug(
                    f"Generated CHF ID '{generated_chf_id}' doesn't match regex '{regex}' "
                    f"(attempt {attempt + 1}/{max_attempts})"
                )

        # If we reach here, we've exhausted all attempts
        error_msg = (
            f"Failed to generate CHF ID matching regex '{regex}' after {max_attempts} attempts. "
            f"Please check if the regex pattern is compatible with prefix '{prefix}' and length {length}."
        )
        logger.error(error_msg)
        raise CHFIDGenerationError(error_msg)

    except Exception as e:
        if isinstance(e, CHFIDGenerationError):
            raise

        error_msg = f"Unexpected error during CHF ID generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise CHFIDGenerationError(error_msg) from e


def generate_identification_code(prefix: str, suffix: str) -> str:
    """
    Generate a unique identification code based on the identification type.
    """
    return f"{prefix}-{generate_random_alphanumeric(10)}-{suffix}"


def get_location_based_insurees(user_location: Location):
    location_ids = user_location.get_descendants(include_self=True).values_list(
        "id", flat=True
    )

    return Insuree.objects.filter(location_id__in=location_ids)
