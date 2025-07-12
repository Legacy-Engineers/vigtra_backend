import os
from .. import BASE_DIR
import logging

logger = logging.getLogger(__name__)

# Supported database engines
SUPPORTED_DATABASE_ENGINES = {
    "sqlite": "django.db.backends.sqlite3",
    "postgresql": "django.db.backends.postgresql",
    "mysql": "django.db.backends.mysql",
}

# Get database engine from environment
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()

# Validate engine
if DB_ENGINE not in SUPPORTED_DATABASE_ENGINES:
    supported = ", ".join(SUPPORTED_DATABASE_ENGINES.keys())
    logger.error(f"Unsupported database engine: {DB_ENGINE}. Supported: {supported}")
    raise ValueError(
        f"Unsupported database engine: {DB_ENGINE}. Supported: {supported}"
    )


def get_database_config():
    """Get database configuration based on engine type."""
    engine = SUPPORTED_DATABASE_ENGINES[DB_ENGINE]

    if DB_ENGINE == "sqlite":
        return {
            "default": {
                "ENGINE": engine,
                "NAME": BASE_DIR / "db.sqlite3",
                # SQLite options
                "OPTIONS": {
                    "timeout": 20,
                },
            }
        }

    elif DB_ENGINE == "postgresql":
        return {
            "default": {
                "ENGINE": engine,
                "NAME": os.getenv("DB_NAME", "postgres"),
                "USER": os.getenv("DB_USER", "postgres"),
                "PASSWORD": os.getenv("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", "localhost"),
                "PORT": os.getenv("DB_PORT", "5432"),
                # PostgreSQL options
                "OPTIONS": {
                    "connect_timeout": 10,
                },
                "CONN_MAX_AGE": 600,  # Connection pooling
            }
        }

    elif DB_ENGINE == "mysql":
        return {
            "default": {
                "ENGINE": engine,
                "NAME": os.getenv("DB_NAME", "mysql"),
                "USER": os.getenv("DB_USER", "root"),
                "PASSWORD": os.getenv("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", "localhost"),
                "PORT": os.getenv("DB_PORT", "3306"),
                # MySQL options
                "OPTIONS": {
                    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                    "charset": "utf8mb4",
                },
                "CONN_MAX_AGE": 600,
            }
        }


# Set database configuration
try:
    DATABASES = get_database_config()
    logger.info(f"Database configured for {DB_ENGINE}")
except Exception as e:
    logger.error(f"Failed to configure database: {e}")
    raise


# Additional database settings
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Database connection health check
def check_database_connection():
    """Simple database connection check."""
    try:
        from django.db import connections

        db_conn = connections["default"]
        db_conn.cursor()
        return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False


# Development vs Production database settings
if os.getenv("DJANGO_ENV") == "production":
    # Production database optimizations
    if DB_ENGINE in ["postgresql", "mysql"]:
        DATABASES["default"]["CONN_MAX_AGE"] = 3600  # Longer connection pooling
        DATABASES["default"]["OPTIONS"]["connect_timeout"] = 30

        # Add read replica if configured
        if os.getenv("DB_READ_HOST"):
            DATABASES["read_replica"] = DATABASES["default"].copy()
            DATABASES["read_replica"]["HOST"] = os.getenv("DB_READ_HOST")
            DATABASES["read_replica"]["USER"] = os.getenv(
                "DB_READ_USER", DATABASES["default"]["USER"]
            )

            # Database router for read/write split
            DATABASE_ROUTERS = ["myproject.routers.DatabaseRouter"]

elif os.getenv("DJANGO_ENV") == "testing":
    # Testing database settings
    if DB_ENGINE == "postgresql":
        DATABASES["default"]["NAME"] = f"test_{DATABASES['default']['NAME']}"
    elif DB_ENGINE == "sqlite":
        DATABASES["default"]["NAME"] = ":memory:"  # In-memory for faster tests


# Log database configuration (without sensitive info)
config_info = {
    "engine": DB_ENGINE,
    "host": DATABASES["default"].get("HOST", "N/A"),
    "port": DATABASES["default"].get("PORT", "N/A"),
    "name": DATABASES["default"].get("NAME", "N/A"),
}
logger.info(f"Database configuration: {config_info}")
