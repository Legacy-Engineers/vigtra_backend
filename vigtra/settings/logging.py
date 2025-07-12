import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment-based configuration
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if ENVIRONMENT == "development" else "INFO")

# Create logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths - Convert to strings for logging handlers
DEBUG_LOG = str(LOGS_DIR / "debug.log")
ERROR_LOG = str(LOGS_DIR / "error.log")
DJANGO_LOG = str(LOGS_DIR / "django.log")
VIGTRA_LOG = str(LOGS_DIR / "vigtra.log")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {funcName}:{lineno} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        # Fixed JSON formatter - escape the braces properly
        "json": {
            "format": '{{"level": "{levelname}", "time": "{asctime}", "logger": "{name}", "message": "{message}"}}',
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        # Console handler - only in development
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["require_debug_true"] if ENVIRONMENT == "production" else [],
        },
        # Debug file handler - all debug info
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DEBUG_LOG,  # Now a string
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        # Error file handler - errors and warnings only
        "error_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": ERROR_LOG,  # Now a string
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        # Django-specific log file
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DJANGO_LOG,  # Now a string
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        # Application-specific log file
        "vigtra_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": VIGTRA_LOG,  # Now a string
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        # Email handler for critical errors in production
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "formatter": "verbose",
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console", "debug_file", "error_file"],
    },
    "loggers": {
        # Django framework logging
        "django": {
            "handlers": ["django_file", "console"]
            if ENVIRONMENT != "production"
            else ["django_file"],
            "level": "INFO",
            "propagate": False,
        },
        # Django database queries (useful for debugging)
        "django.db.backends": {
            "handlers": ["debug_file"],
            "level": "DEBUG" if ENVIRONMENT == "development" else "INFO",
            "propagate": False,
        },
        # Django security issues
        "django.security": {
            "handlers": ["error_file", "mail_admins"]
            if ENVIRONMENT == "production"
            else ["error_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        # Application logging
        "vigtra": {
            "handlers": ["vigtra_file", "console"]
            if ENVIRONMENT != "production"
            else ["vigtra_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # Third-party libraries
        "urllib3": {
            "handlers": ["debug_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "requests": {
            "handlers": ["debug_file"],
            "level": "WARNING",
            "propagate": False,
        },
        # GraphQL logging
        "graphene": {
            "handlers": ["vigtra_file", "console"]
            if ENVIRONMENT != "production"
            else ["vigtra_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Production-specific adjustments
if ENVIRONMENT == "production":
    # Use JSON formatter for production logs (better for log aggregation)
    LOGGING["handlers"]["vigtra_file"]["formatter"] = "json"
    LOGGING["handlers"]["django_file"]["formatter"] = "json"

    # Add syslog handler for production
    LOGGING["handlers"]["syslog"] = {
        "level": "INFO",
        "class": "logging.handlers.SysLogHandler",
        "address": "/dev/log",
        "formatter": "json",
    }

    # Add syslog to root handlers
    LOGGING["root"]["handlers"].append("syslog")

# Development-specific adjustments
elif ENVIRONMENT == "development":
    # More verbose SQL logging in development
    LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"

    # Add rich console handler if available
    try:
        import rich.logging  # Import first to check availability

        LOGGING["handlers"]["rich_console"] = {
            "level": "DEBUG",
            "class": "rich.logging.RichHandler",
            "formatter": "simple",
            "rich_tracebacks": True,
        }
        # Replace console handler with rich handler
        for logger_config in LOGGING["loggers"].values():
            if "console" in logger_config.get("handlers", []):
                logger_config["handlers"] = [
                    h if h != "console" else "rich_console"
                    for h in logger_config["handlers"]
                ]
    except ImportError:
        pass  # Rich not available, use standard console

# Testing environment
elif ENVIRONMENT == "testing":
    # Simpler logging for tests
    LOGGING["handlers"] = {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    }
    LOGGING["root"]["handlers"] = ["console"]
    for logger_config in LOGGING["loggers"].values():
        logger_config["handlers"] = ["console"]
        logger_config["level"] = "WARNING"
