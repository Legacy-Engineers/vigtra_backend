"""
Advanced caching strategy configuration
"""
import os
from django.core.cache.utils import make_template_fragment_key

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'short': 300,      # 5 minutes
    'medium': 1800,    # 30 minutes  
    'long': 3600,      # 1 hour
    'very_long': 86400, # 24 hours
}

# View-level caching configuration
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = CACHE_TIMEOUTS['medium']
CACHE_MIDDLEWARE_KEY_PREFIX = 'vigtra_page'

# Template fragment caching
TEMPLATE_FRAGMENT_CACHE_TIMEOUT = CACHE_TIMEOUTS['long']

# Model-specific cache settings
MODEL_CACHE_SETTINGS = {
    'User': {
        'timeout': CACHE_TIMEOUTS['medium'],
        'key_prefix': 'user',
        'cache_relations': True,
    },
    'Location': {
        'timeout': CACHE_TIMEOUTS['very_long'],  # Locations change rarely
        'key_prefix': 'location',
        'cache_relations': True,
    },
    'HealthFacility': {
        'timeout': CACHE_TIMEOUTS['long'],
        'key_prefix': 'facility',
        'cache_relations': True,
    },
    'Insuree': {
        'timeout': CACHE_TIMEOUTS['medium'],
        'key_prefix': 'insuree',
        'cache_relations': True,
    },
    'Policy': {
        'timeout': CACHE_TIMEOUTS['medium'],
        'key_prefix': 'policy',
        'cache_relations': True,
    },
    'Claim': {
        'timeout': CACHE_TIMEOUTS['short'],  # Claims change frequently
        'key_prefix': 'claim',
        'cache_relations': True,
    },
}

# API response caching
API_CACHE_SETTINGS = {
    'default_timeout': CACHE_TIMEOUTS['medium'],
    'authenticated_timeout': CACHE_TIMEOUTS['short'],
    'public_timeout': CACHE_TIMEOUTS['long'],
}

# GraphQL query caching
GRAPHQL_CACHE_SETTINGS = {
    'enable_caching': True,
    'default_timeout': CACHE_TIMEOUTS['medium'],
    'introspection_timeout': CACHE_TIMEOUTS['very_long'],
    'max_query_depth': 10,
}

# Cache invalidation patterns
CACHE_INVALIDATION_PATTERNS = {
    'user_update': ['user_*', 'profile_*', 'auth_*'],
    'location_update': ['location_*', 'facility_*', 'region_*'],
    'policy_update': ['policy_*', 'insuree_*', 'coverage_*'],
    'claim_update': ['claim_*', 'payment_*', 'reimbursement_*'],
}

# Cache warming configuration
CACHE_WARMING_ENABLED = os.getenv('CACHE_WARMING_ENABLED', 'False').lower() == 'true'
CACHE_WARMING_TASKS = [
    'warm_location_cache',
    'warm_facility_cache', 
    'warm_user_permissions_cache',
] if CACHE_WARMING_ENABLED else []

# Redis-specific optimizations
if os.getenv('CACHE_BACKEND', 'redis').lower() == 'redis':
    # Connection pooling
    REDIS_CONNECTION_POOL_KWARGS = {
        'max_connections': 50,
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {},
    }
    
    # Compression for large objects
    REDIS_COMPRESS_THRESHOLD = 1024  # Compress objects larger than 1KB
    
    # Key expiration policies
    REDIS_KEY_PATTERNS = {
        'session:*': CACHE_TIMEOUTS['long'],
        'user:*': CACHE_TIMEOUTS['medium'], 
        'location:*': CACHE_TIMEOUTS['very_long'],
        'temp:*': CACHE_TIMEOUTS['short'],
    }

# Cache monitoring settings
CACHE_MONITORING = {
    'track_hit_rate': True,
    'log_slow_operations': True,
    'slow_operation_threshold': 0.1,  # 100ms
    'monitor_memory_usage': True,
}

# Development cache settings
if os.getenv('DJANGO_ENV', 'development') == 'development':
    # Shorter timeouts for development
    CACHE_TIMEOUTS = {k: min(v, 300) for k, v in CACHE_TIMEOUTS.items()}
    CACHE_MIDDLEWARE_SECONDS = 60  # 1 minute
    
# Cache key generators
def generate_model_cache_key(model_name, obj_id, extra=None):
    """Generate standardized cache key for model instances"""
    key = f"{MODEL_CACHE_SETTINGS.get(model_name, {}).get('key_prefix', model_name.lower())}:{obj_id}"
    if extra:
        key += f":{extra}"
    return key

def generate_queryset_cache_key(model_name, filters=None, ordering=None):
    """Generate cache key for querysets"""
    import hashlib
    key_parts = [model_name.lower(), 'qs']
    
    if filters:
        filter_str = str(sorted(filters.items())) if isinstance(filters, dict) else str(filters)
        key_parts.append(hashlib.md5(filter_str.encode()).hexdigest()[:8])
    
    if ordering:
        key_parts.append(f"order_{hashlib.md5(str(ordering).encode()).hexdigest()[:8]}")
    
    return ':'.join(key_parts)

def generate_api_cache_key(endpoint, params=None, user_id=None):
    """Generate cache key for API responses"""
    import hashlib
    key_parts = ['api', endpoint.replace('/', '_')]
    
    if user_id:
        key_parts.append(f"user_{user_id}")
    
    if params:
        param_str = str(sorted(params.items())) if isinstance(params, dict) else str(params)
        key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])
    
    return ':'.join(key_parts)