import os
from .. import BASE_DIR

SUPPORTED_DATABASE_ENGINES = [
    "django.db.backends.sqlite3",
    "django.db.backends.postgresql",
]

SERVER_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

if SERVER_ENGINE not in SUPPORTED_DATABASE_ENGINES:
    raise ValueError(f"Unsupported database engine: {SERVER_ENGINE}")

if SERVER_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif SERVER_ENGINE == "django.db.backends.postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
