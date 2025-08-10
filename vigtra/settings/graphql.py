import os
import logging
import secrets
from datetime import timedelta

SECRET_KEY = secrets.token_urlsafe(50)

logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
GRAPHQL_DEBUG = (
    os.getenv(
        "GRAPHQL_DEBUG", "true" if ENVIRONMENT == "development" else "false"
    ).lower()
    == "true"
)

# GraphQL endpoint configuration
GRAPHQL_URL = os.getenv("GRAPHQL_URL", "/graphql/")
GRAPHIQL_URL = os.getenv("GRAPHIQL_URL", "/graphiql/")

# Base middleware - only include what exists
GRAPHQL_MIDDLEWARE = [
    "graphql_jwt.middleware.JSONWebTokenMiddleware",
]

# Add environment-specific middleware
if ENVIRONMENT == "development":
    GRAPHQL_MIDDLEWARE.extend(
        [
            "graphene_django.debug.DjangoDebugMiddleware",
            # Remove custom middleware that doesn't exist yet
            # "modules.core.middleware.GraphQLPerformanceMiddleware",
        ]
    )

elif ENVIRONMENT == "production":
    # Only add middleware that actually exists
    GRAPHQL_MIDDLEWARE.extend(
        [
            # "modules.core.middleware.GraphQLSecurityMiddleware",
            # "modules.core.middleware.GraphQLRateLimitMiddleware",
            # "modules.core.middleware.GraphQLLoggingMiddleware",
        ]
    )

# Query complexity and depth limits
GRAPHQL_QUERY_MAX_COMPLEXITY = int(os.getenv("GRAPHQL_MAX_COMPLEXITY", "1000"))
GRAPHQL_QUERY_MAX_DEPTH = int(os.getenv("GRAPHQL_MAX_DEPTH", "10"))

# Rate limiting
GRAPHQL_RATE_LIMIT_PER_MINUTE = int(os.getenv("GRAPHQL_RATE_LIMIT", "60"))

GRAPHENE = {
    "SCHEMA": "modules.core.schema.schema",
    "MIDDLEWARE": GRAPHQL_MIDDLEWARE,
    # Schema configuration
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
    # Introspection (disable in production for security)
    "INTROSPECTION": GRAPHQL_DEBUG,
    # Query validation
    "MAX_QUERY_COMPLEXITY": GRAPHQL_QUERY_MAX_COMPLEXITY,
    "MAX_QUERY_DEPTH": GRAPHQL_QUERY_MAX_DEPTH,
    # Relay support
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100,
    # Error handling
    "HANDLE_ERRORS": True,
    "PRETTY": GRAPHQL_DEBUG,
    # Subscription settings (if using channels)
    "SUBSCRIPTION_PATH": "/graphql/subscriptions/",
    # Custom context (only if you create this function)
    # "CONTEXT": "modules.core.graphql.context.get_context",
}


# CORS settings for GraphQL
if ENVIRONMENT == "development":
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/graphql.*$"

GRAPHQL_JWT = {
    # Auto-generate temporary JWT secret for development
    "JWT_SECRET_KEY": secrets.token_urlsafe(32),
    # Token expiration settings
    "JWT_EXPIRATION_DELTA": timedelta(minutes=60),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_VERIFY_EXPIRATION": True,
    # Refresh token settings (fully enabled)
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_TOKEN_N_BYTES": 20,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_DELETE_STALE_BLACKLISTED_TOKENS": True,
    # Authentication settings
    "JWT_AUTH_HEADER_TYPES": ("Bearer",),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_VERIFY": True,
    "JWT_ALGORITHM": "HS256",
    # Cookie settings for web clients
    "JWT_COOKIE_NAME": "jwt-token",
    "JWT_COOKIE_SECURE": False,  # False for development (HTTP)
    "JWT_COOKIE_HTTP_ONLY": True,
    "JWT_COOKIE_SAMESITE": "Lax",
    # Additional settings for refresh tokens
    "JWT_BLACKLIST_ENABLED": True,
    "JWT_BLACKLIST_TOKEN_CHECKS": ["refresh"],
    "JWT_REFRESH_TOKEN_MODEL": "graphql_jwt.RefreshToken",
}

logger.info(f"GraphQL configured for {ENVIRONMENT} environment")
logger.info(f"GraphQL Debug: {GRAPHQL_DEBUG}")
logger.info(f"GraphQL Introspection: {GRAPHENE['INTROSPECTION']}")
