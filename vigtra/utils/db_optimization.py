"""
Database optimization utilities
"""
from django.db import models
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cached_queryset(timeout=300):
    """
    Decorator to cache queryset results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"qs_{func.__name__}_{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                # Convert queryset to list for caching
                if hasattr(result, '__iter__') and hasattr(result, 'model'):
                    result = list(result)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def optimize_queryset(queryset, select_related_fields=None, prefetch_related_fields=None):
    """
    Apply common query optimizations to a queryset
    """
    if select_related_fields:
        queryset = queryset.select_related(*select_related_fields)
    
    if prefetch_related_fields:
        queryset = queryset.prefetch_related(*prefetch_related_fields)
    
    return queryset


class OptimizedModelMixin:
    """
    Mixin to add optimization methods to models
    """
    
    @classmethod
    def get_optimized_queryset(cls, select_related=None, prefetch_related=None):
        """
        Get an optimized queryset with common joins
        """
        queryset = cls.objects.all()
        
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset
    
    @classmethod
    def bulk_create_optimized(cls, objects, batch_size=1000):
        """
        Optimized bulk create with batching
        """
        return cls.objects.bulk_create(objects, batch_size=batch_size)
    
    @classmethod
    def bulk_update_optimized(cls, objects, fields, batch_size=1000):
        """
        Optimized bulk update with batching
        """
        return cls.objects.bulk_update(objects, fields, batch_size=batch_size)


def get_database_stats():
    """
    Get database performance statistics
    """
    from django.db import connection
    
    stats = {
        'total_queries': len(connection.queries),
        'queries': connection.queries[-10:] if connection.queries else [],  # Last 10 queries
    }
    
    # Calculate query time statistics
    if connection.queries:
        query_times = [float(q['time']) for q in connection.queries]
        stats.update({
            'total_time': sum(query_times),
            'avg_time': sum(query_times) / len(query_times),
            'max_time': max(query_times),
            'slow_queries': [q for q in connection.queries if float(q['time']) > 0.1]
        })
    
    return stats


def analyze_model_queries(model_class):
    """
    Analyze common queries for a model and suggest optimizations
    """
    from django.db import connection
    
    # Get model meta information
    model_name = model_class._meta.model_name
    table_name = model_class._meta.db_table
    
    suggestions = []
    
    # Check for foreign key relationships
    fk_fields = [f.name for f in model_class._meta.fields if f.many_to_one]
    if fk_fields:
        suggestions.append(f"Consider using select_related({', '.join(fk_fields)}) for {model_name}")
    
    # Check for reverse foreign key relationships
    reverse_fk_fields = [f.get_accessor_name() for f in model_class._meta.related_objects]
    if reverse_fk_fields:
        suggestions.append(f"Consider using prefetch_related({', '.join(reverse_fk_fields)}) for {model_name}")
    
    # Check for missing indexes
    indexed_fields = [f.name for f in model_class._meta.fields if f.db_index]
    all_fields = [f.name for f in model_class._meta.fields]
    
    # Suggest indexes for commonly filtered fields
    common_filter_fields = ['created_at', 'updated_at', 'status', 'is_active', 'user_id']
    for field in common_filter_fields:
        if field in all_fields and field not in indexed_fields:
            suggestions.append(f"Consider adding db_index=True to {model_name}.{field}")
    
    return {
        'model': model_name,
        'table': table_name,
        'suggestions': suggestions,
        'foreign_keys': fk_fields,
        'reverse_foreign_keys': reverse_fk_fields,
        'indexed_fields': indexed_fields
    }