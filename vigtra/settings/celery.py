import os

CACHE_BACKEND = os.getenv(
    "CACHE_BACKEND", "django.core.cache.backends.memcached.PyMemcacheCache"
)
CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379/1")


if CACHE_BACKEND:
    CACHES = {
        "default": {
            "BACKEND": CACHE_BACKEND,
            "LOCATION": CACHE_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PARSER_CLASS": "redis.connection.HiredisParser",
            },
            "KEY_PREFIX": "vigtra",
        }
    }
