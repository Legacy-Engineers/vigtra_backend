#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import logging

logger = logging.getLogger(__name__)


def main():
    """Run administrative tasks."""

    SERVER_ENV = os.getenv("SERVER_ENV", "dev")
    if SERVER_ENV == "dev":
        os.environ["DJANGO_SETTINGS_MODULE"] = "vigtra.settings.dev"
    elif SERVER_ENV == "prod":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vigtra.settings.prod")
    else:
        logger.error("Invalid SERVER_ENV value. Use 'dev' or 'prod'.")
        sys.exit(1)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
