"""
Performance monitoring middleware
"""
import time
import logging
from django.db import connection
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware:
    """
    Middleware to monitor request performance and database queries
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        end_time = time.time()
        total_time = end_time - start_time
        total_queries = len(connection.queries) - start_queries
        
        # Log slow requests (> 1 second)
        if total_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {total_time:.2f}s with {total_queries} queries"
            )
        
        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-Response-Time'] = f"{total_time:.3f}s"
            response['X-DB-Queries'] = str(total_queries)
        
        # Track performance metrics in cache for monitoring
        if not settings.DEBUG:
            cache_key = f"perf_metrics:{request.path}"
            metrics = cache.get(cache_key, {'count': 0, 'total_time': 0, 'total_queries': 0})
            metrics['count'] += 1
            metrics['total_time'] += total_time
            metrics['total_queries'] += total_queries
            cache.set(cache_key, metrics, 3600)  # Store for 1 hour
        
        return response


class DatabaseQueryCountMiddleware:
    """
    Middleware to limit database queries per request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_queries = getattr(settings, 'MAX_DB_QUERIES_PER_REQUEST', 50)

    def __call__(self, request):
        start_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        total_queries = len(connection.queries) - start_queries
        
        if total_queries > self.max_queries:
            logger.error(
                f"Too many DB queries: {request.method} {request.path} "
                f"executed {total_queries} queries (limit: {self.max_queries})"
            )
        
        return response


class CacheHitRateMiddleware:
    """
    Middleware to track cache hit rates
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track cache operations during request
        cache_hits = 0
        cache_misses = 0
        
        # Monkey patch cache.get to track hits/misses
        original_get = cache.get
        
        def tracked_get(key, default=None, version=None):
            nonlocal cache_hits, cache_misses
            result = original_get(key, default, version)
            if result is not None and result != default:
                cache_hits += 1
            else:
                cache_misses += 1
            return result
        
        cache.get = tracked_get
        
        try:
            response = self.get_response(request)
        finally:
            # Restore original method
            cache.get = original_get
        
        # Log cache statistics
        total_cache_ops = cache_hits + cache_misses
        if total_cache_ops > 0:
            hit_rate = (cache_hits / total_cache_ops) * 100
            if hit_rate < 80:  # Log if hit rate is below 80%
                logger.info(
                    f"Cache hit rate: {hit_rate:.1f}% for {request.path} "
                    f"({cache_hits} hits, {cache_misses} misses)"
                )
        
        return response