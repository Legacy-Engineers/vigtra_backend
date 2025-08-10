import os
import logging
from ..extra_settings import ExtraSettings

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "redis").lower()
CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379/1")
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "300"))  # 5 minutes default

# Supported cache backends
CACHE_BACKENDS = {
    "redis": "django_redis.cache.RedisCache",
    "memcached": "django.core.cache.backends.memcached.PyMemcacheCache",
    "dummy": "django.core.cache.backends.dummy.DummyCache",
    "locmem": "django.core.cache.backends.locmem.LocMemCache",
    "database": "django.core.cache.backends.db.DatabaseCache",
    "filebased": "django.core.cache.backends.filebased.FileBasedCache",
}

EXTRA_CACHE_SETTINGS = ExtraSettings.get_extra_cache_settings()


def get_cache_config():
    """Get cache configuration based on backend type."""

    if CACHE_BACKEND not in CACHE_BACKENDS:
        logger.warning(
            f"Unknown cache backend: {CACHE_BACKEND}, falling back to dummy cache"
        )
        return get_dummy_cache()

    backend_class = CACHE_BACKENDS[CACHE_BACKEND]

    # Redis configuration
    if CACHE_BACKEND == "redis":
        return {
            "default": {
                "BACKEND": backend_class,
                "LOCATION": CACHE_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {
                        "max_connections": 50,
                        "retry_on_timeout": True,
                    },
                    "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
                    "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                },
                "KEY_PREFIX": "vigtra",
                "VERSION": 1,
                "TIMEOUT": CACHE_TIMEOUT,
            }
        }

    # Memcached configuration
    elif CACHE_BACKEND == "memcached":
        # Parse memcached URL (format: memcached://host:port)
        location = CACHE_URL.replace("memcached://", "").replace("redis://", "")
        return {
            "default": {
                "BACKEND": backend_class,
                "LOCATION": location,
                "OPTIONS": {
                    "server_max_value_length": 1024 * 1024 * 2,  # 2MB
                },
                "KEY_PREFIX": "vigtra",
                "VERSION": 1,
                "TIMEOUT": CACHE_TIMEOUT,
            }
        }

    # Database cache
    elif CACHE_BACKEND == "database":
        return {
            "default": {
                "BACKEND": backend_class,
                "LOCATION": "cache_table",  # Table name
                "KEY_PREFIX": "vigtra",
                "VERSION": 1,
                "TIMEOUT": CACHE_TIMEOUT,
            }
        }

    # File-based cache
    elif CACHE_BACKEND == "filebased":
        from pathlib import Path

        cache_dir = Path(__file__).resolve().parent.parent.parent / "cache"
        cache_dir.mkdir(exist_ok=True)

        return {
            "default": {
                "BACKEND": backend_class,
                "LOCATION": str(cache_dir),
                "KEY_PREFIX": "vigtra",
                "VERSION": 1,
                "TIMEOUT": CACHE_TIMEOUT,
                "OPTIONS": {
                    "MAX_ENTRIES": 1000,
                },
            }
        }

    # Local memory cache
    elif CACHE_BACKEND == "locmem":
        return {
            "default": {
                "BACKEND": backend_class,
                "LOCATION": "vigtra-cache",
                "KEY_PREFIX": "vigtra",
                "VERSION": 1,
                "TIMEOUT": CACHE_TIMEOUT,
                "OPTIONS": {
                    "MAX_ENTRIES": 1000,
                },
            }
        }

    # Dummy cache (no caching)
    else:
        return get_dummy_cache()


def get_dummy_cache():
    """Dummy cache configuration for development/testing."""
    return {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


# Multi-tier cache setup for production
def get_multi_tier_cache():
    """Multi-level cache with local memory + Redis."""
    default_cache = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 50},
            },
            "KEY_PREFIX": "vigtra",
            "TIMEOUT": CACHE_TIMEOUT,
        },
        "locmem": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "vigtra-local",
            "TIMEOUT": 60,  # Short timeout for local cache
            "OPTIONS": {
                "MAX_ENTRIES": 500,
            },
        },
        "sessions": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_URL.replace("/1", "/2"),  # Different Redis DB
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "vigtra_session",
            "TIMEOUT": 3600,  # 1 hour for sessions
        },
    }

    for cache_name, cache_config in EXTRA_CACHE_SETTINGS.items():
        default_cache[cache_name] = {
            "BACKEND": cache_config["backend"],
            "LOCATION": CACHE_URL,
            "OPTIONS": cache_config["options"],
            "KEY_PREFIX": cache_config["key_prefix"],
            "TIMEOUT": cache_config["timeout"],
        }

    return default_cache


# Environment-based cache configuration
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")

try:
    if ENVIRONMENT == "production" and CACHE_BACKEND == "redis":
        # Use multi-tier cache in production
        CACHES = get_multi_tier_cache()

        # Session cache configuration
        SESSION_ENGINE = "django.contrib.sessions.backends.cache"
        SESSION_CACHE_ALIAS = "sessions"

    elif ENVIRONMENT == "testing":
        # Use dummy cache for testing
        CACHES = get_dummy_cache()

    else:
        # Standard single cache
        CACHES = get_cache_config()

    # Cache health check
    def check_cache_connection():
        """Test cache connection."""
        try:
            from django.core.cache import cache

            cache.set("health_check", "ok", 30)
            result = cache.get("health_check")
            return result == "ok"
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")
            return False

    logger.info(
        f"Cache configured: {CACHE_BACKEND} at {CACHE_URL.split('@')[-1] if '@' in CACHE_URL else CACHE_URL}"
    )

except Exception as e:
    logger.error(f"Cache configuration failed: {e}")
    # Fallback to dummy cache
    CACHES = get_dummy_cache()

# Cache key versioning for deployments
CACHE_MIDDLEWARE_KEY_PREFIX = "vigtra"
CACHE_MIDDLEWARE_SECONDS = CACHE_TIMEOUT

# Additional cache settings
if CACHE_BACKEND == "redis":
    # Use Redis for sessions too
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # Cache template loading in production
    if ENVIRONMENT == "production":
        TEMPLATE_CACHE_TIMEOUT = 3600  # 1 hour
