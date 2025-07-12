import os
import logging

logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")
GRAPHQL_DEBUG = (
    os.getenv(
        "GRAPHQL_DEBUG", "true" if ENVIRONMENT == "development" else "false"
    ).lower()
    == "true"
)

# GraphQL endpoint configuration
GRAPHQL_URL = os.getenv("GRAPHQL_URL", "/graphql/")
GRAPHIQL_URL = os.getenv("GRAPHIQL_URL", "/graphiql/")

# Base middleware
GRAPHQL_MIDDLEWARE = [
    "graphql_jwt.middleware.JSONWebTokenMiddleware",
]

# Add environment-specific middleware
if ENVIRONMENT == "development":
    GRAPHQL_MIDDLEWARE.extend(
        [
            "graphene_django.debug.DjangoDebugMiddleware",
            # Add performance middleware for development
            "modules.core.middleware.GraphQLPerformanceMiddleware",
        ]
    )

elif ENVIRONMENT == "production":
    GRAPHQL_MIDDLEWARE.extend(
        [
            # Production middleware
            "modules.core.middleware.GraphQLSecurityMiddleware",
            "modules.core.middleware.GraphQLRateLimitMiddleware",
            "modules.core.middleware.GraphQLLoggingMiddleware",
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
    "SCHEMA_OUTPUT": "schema.json",  # For schema export
    "SCHEMA_INDENT": 2,
    # Execution settings
    "EXECUTOR": "graphql.execution.executors.asyncio.AsyncioExecutor"
    if ENVIRONMENT == "production"
    else None,
    # Introspection (disable in production for security)
    "INTROSPECTION": GRAPHQL_DEBUG,
    # Query validation
    "MAX_QUERY_COMPLEXITY": GRAPHQL_QUERY_MAX_COMPLEXITY,
    "MAX_QUERY_DEPTH": GRAPHQL_QUERY_MAX_DEPTH,
    # Relay support
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100,
    # Apollo Tracing (for performance monitoring)
    "APOLLO_TRACING": ENVIRONMENT == "development",
    # Error handling
    "HANDLE_ERRORS": True,
    "PRETTY": GRAPHQL_DEBUG,
    # Subscription settings (if using channels)
    "SUBSCRIPTION_PATH": "/graphql/subscriptions/",
    # Custom context
    "CONTEXT": "modules.core.graphql.context.get_context",
}

# GraphQL JWT settings
GRAPHQL_JWT = {
    "JWT_ALGORITHM": "HS256",
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_LEEWAY": 0,
    "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY")),
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": os.getenv("JWT_EXPIRATION_MINUTES", 60),  # minutes
    "JWT_REFRESH_EXPIRATION_DELTA": os.getenv("JWT_REFRESH_DAYS", 7),  # days
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_TOKEN_N_BYTES": 20,
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    # Cookie settings for web clients
    "JWT_COOKIE_NAME": "jwt-token",
    "JWT_COOKIE_SECURE": ENVIRONMENT == "production",
    "JWT_COOKIE_HTTP_ONLY": True,
    "JWT_COOKIE_SAMESITE": "Lax",
    # Token refresh settings
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_DELETE_STALE_BLACKLISTED_TOKENS": True,
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

# GraphiQL settings (GraphQL IDE)
GRAPHIQL_SETTINGS = {
    "enabled": GRAPHQL_DEBUG,
    "endpoint": GRAPHQL_URL,
    "subscriptions_endpoint": GRAPHENE.get("SUBSCRIPTION_PATH"),
    "headers_editor": True,
    "query_editor": True,
    "variables_editor": True,
    "prettify": True,
    "explorer": True,
}

# File upload settings for GraphQL
GRAPHQL_UPLOAD_MAX_SIZE = (
    int(os.getenv("GRAPHQL_UPLOAD_MAX_SIZE", "50")) * 1024 * 1024
)  # 50MB default
GRAPHQL_UPLOAD_MAX_FILES = int(os.getenv("GRAPHQL_UPLOAD_MAX_FILES", "10"))

# Performance monitoring
if ENVIRONMENT == "production":
    # Apollo Studio integration
    APOLLO_STUDIO_API_KEY = os.getenv("APOLLO_STUDIO_API_KEY")
    if APOLLO_STUDIO_API_KEY:
        GRAPHENE["APOLLO_STUDIO"] = {
            "API_KEY": APOLLO_STUDIO_API_KEY,
            "GRAPH_REF": os.getenv("APOLLO_GRAPH_REF", "production"),
        }

# Error handling configuration
GRAPHQL_ERROR_HANDLER = "modules.core.graphql.errors.custom_error_handler"

# Security headers for GraphQL endpoint
GRAPHQL_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

# Query logging (only in development or when explicitly enabled)
GRAPHQL_QUERY_LOGGING = os.getenv("GRAPHQL_QUERY_LOGGING", "false").lower() == "true"

# Schema caching
GRAPHQL_SCHEMA_CACHE_TIMEOUT = int(
    os.getenv("GRAPHQL_SCHEMA_CACHE_TIMEOUT", "3600")
)  # 1 hour

# Playground settings (alternative to GraphiQL)
GRAPHQL_PLAYGROUND = {
    "enabled": ENVIRONMENT == "development",
    "endpoint": GRAPHQL_URL,
    "subscriptions_endpoint": GRAPHENE.get("SUBSCRIPTION_PATH"),
    "settings": {
        "editor.theme": "dark",
        "editor.fontFamily": "JetBrains Mono, Monaco, monospace",
        "editor.fontSize": 14,
        "request.credentials": "include",
    },
}

# Validation rules
GRAPHQL_VALIDATION_RULES = [
    "graphql.validation.rules.specified_rules.ExecutableDefinitionsRule",
    "graphql.validation.rules.specified_rules.FieldsOnCorrectTypeRule",
    "graphql.validation.rules.specified_rules.FragmentsOnCompositeTypesRule",
    "graphql.validation.rules.specified_rules.KnownArgumentNamesRule",
    "graphql.validation.rules.specified_rules.KnownDirectivesRule",
    "graphql.validation.rules.specified_rules.KnownFragmentNamesRule",
    "graphql.validation.rules.specified_rules.KnownTypeNamesRule",
    "graphql.validation.rules.specified_rules.LoneAnonymousOperationRule",
    "graphql.validation.rules.specified_rules.NoFragmentCyclesRule",
    "graphql.validation.rules.specified_rules.NoUndefinedVariablesRule",
    "graphql.validation.rules.specified_rules.NoUnusedFragmentsRule",
    "graphql.validation.rules.specified_rules.NoUnusedVariablesRule",
    "graphql.validation.rules.specified_rules.OverlappingFieldsCanBeMergedRule",
    "graphql.validation.rules.specified_rules.PossibleFragmentSpreadsRule",
    "graphql.validation.rules.specified_rules.ProvidedRequiredArgumentsRule",
    "graphql.validation.rules.specified_rules.ScalarLeafsRule",
    "graphql.validation.rules.specified_rules.SingleFieldSubscriptionsRule",
    "graphql.validation.rules.specified_rules.UniqueArgumentNamesRule",
    "graphql.validation.rules.specified_rules.UniqueDirectivesPerLocationRule",
    "graphql.validation.rules.specified_rules.UniqueFragmentNamesRule",
    "graphql.validation.rules.specified_rules.UniqueInputFieldNamesRule",
    "graphql.validation.rules.specified_rules.UniqueOperationNamesRule",
    "graphql.validation.rules.specified_rules.UniqueVariableNamesRule",
    "graphql.validation.rules.specified_rules.VariablesAreInputTypesRule",
    "graphql.validation.rules.specified_rules.VariablesInAllowedPositionRule",
]

# Add custom validation rules
if ENVIRONMENT == "production":
    GRAPHQL_VALIDATION_RULES.extend(
        [
            "modules.core.graphql.validation.QueryComplexityRule",
            "modules.core.graphql.validation.QueryDepthRule",
            "modules.core.graphql.validation.RateLimitRule",
        ]
    )

logger.info(f"GraphQL configured for {ENVIRONMENT} environment")
logger.info(f"GraphQL Debug: {GRAPHQL_DEBUG}")
logger.info(f"GraphQL Introspection: {GRAPHENE['INTROSPECTION']}")
