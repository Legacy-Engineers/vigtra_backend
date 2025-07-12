#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import logging

# Set up basic logging before Django is loaded
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_settings_module():
    """Determine the appropriate settings module based on environment."""

    # Priority order: DJANGO_SETTINGS_MODULE > ENVIRONMENT > default
    if "DJANGO_SETTINGS_MODULE" in os.environ:
        return os.environ["DJANGO_SETTINGS_MODULE"]

    # Map environment names to settings modules
    ENV_SETTINGS_MAP = {
        "dev": "vigtra.settings.development",
        "development": "vigtra.settings.development",
        "local": "vigtra.settings.development",
        "test": "vigtra.settings.testing",
        "testing": "vigtra.settings.testing",
        "stage": "vigtra.settings.staging",
        "staging": "vigtra.settings.staging",
        "prod": "vigtra.settings.production",
        "production": "vigtra.settings.production",
    }

    environment = os.getenv("ENVIRONMENT", "dev").lower()

    if environment in ENV_SETTINGS_MAP:
        return ENV_SETTINGS_MAP[environment]
    else:
        logger.error(f"Invalid ENVIRONMENT: '{environment}'")
        logger.error(f"Valid options: {', '.join(ENV_SETTINGS_MAP.keys())}")
        sys.exit(1)


def check_environment():
    """Perform basic environment checks."""

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)

    # Check if we're in a virtual environment (recommended)
    if not hasattr(sys, "real_prefix") and not sys.base_prefix != sys.prefix:
        logger.warning("Not running in a virtual environment")

    # Check critical environment variables
    if os.getenv("SECRET_KEY") is None and os.getenv("ENVIRONMENT", "dev") != "dev":
        logger.warning("SECRET_KEY environment variable not set")


def main():
    """Run administrative tasks."""

    try:
        # Perform environment checks
        check_environment()

        # Set Django settings module
        settings_module = get_settings_module()
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

        logger.info(f"Using settings: {settings_module}")

        # Import and execute Django management command
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            error_msg = (
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
            logger.error(error_msg)
            raise ImportError(error_msg) from exc

        # Special handling for common commands
        if len(sys.argv) > 1:
            command = sys.argv[1]

            # Show helpful info for runserver
            if command == "runserver":
                env = os.getenv("ENVIRONMENT", "dev")
                logger.info(f"Starting development server in '{env}' environment")

                # Warn about production settings in development
                if "production" in settings_module and env in ["dev", "development"]:
                    logger.warning("Using production settings in development!")

            # Warn about dangerous commands in production
            elif command in ["flush", "reset_db", "loaddata"] and "prod" in os.getenv(
                "ENVIRONMENT", ""
            ):
                response = input(
                    f"Are you sure you want to run '{command}' in production? (yes/no): "
                )
                if response.lower() != "yes":
                    logger.info("Command cancelled")
                    sys.exit(0)

        # Execute the management command
        execute_from_command_line(sys.argv)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if os.getenv("DEBUG", "").lower() == "true":
            raise  # Re-raise in debug mode for full traceback
        sys.exit(1)


if __name__ == "__main__":
    main()
