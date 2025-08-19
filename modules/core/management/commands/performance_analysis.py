"""
Management command to analyze application performance
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import json
from vigtra.utils.db_optimization import analyze_model_queries, get_database_stats


class Command(BaseCommand):
    help = 'Analyze application performance and suggest optimizations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            action='store_true',
            help='Analyze model queries and relationships',
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Analyze cache performance',
        )
        parser.add_argument(
            '--database',
            action='store_true',
            help='Analyze database performance',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all performance analyses',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='console',
            choices=['console', 'json', 'file'],
            help='Output format',
        )

    def handle(self, *args, **options):
        results = {}
        
        if options['all'] or options['models']:
            self.stdout.write(self.style.SUCCESS('Analyzing models...'))
            results['models'] = self.analyze_models()
        
        if options['all'] or options['cache']:
            self.stdout.write(self.style.SUCCESS('Analyzing cache performance...'))
            results['cache'] = self.analyze_cache()
        
        if options['all'] or options['database']:
            self.stdout.write(self.style.SUCCESS('Analyzing database performance...'))
            results['database'] = self.analyze_database()
        
        # Output results
        if options['output'] == 'json':
            self.stdout.write(json.dumps(results, indent=2, default=str))
        elif options['output'] == 'file':
            filename = f'performance_analysis_{int(time.time())}.json'
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f'Results saved to {filename}')
        else:
            self.display_console_results(results)

    def analyze_models(self):
        """Analyze all models for optimization opportunities"""
        model_analyses = {}
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if hasattr(model, '_meta'):
                    analysis = analyze_model_queries(model)
                    model_analyses[f"{app_config.label}.{model.__name__}"] = analysis
        
        return model_analyses

    def analyze_cache(self):
        """Analyze cache performance"""
        cache_stats = {
            'backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'Unknown'),
            'location': getattr(settings, 'CACHES', {}).get('default', {}).get('LOCATION', 'Unknown'),
        }
        
        # Test cache performance
        test_key = 'performance_test'
        test_data = {'test': True, 'timestamp': time.time()}
        
        # Write performance
        start_time = time.time()
        cache.set(test_key, test_data, 60)
        write_time = time.time() - start_time
        
        # Read performance  
        start_time = time.time()
        retrieved_data = cache.get(test_key)
        read_time = time.time() - start_time
        
        cache_stats.update({
            'write_time_ms': round(write_time * 1000, 2),
            'read_time_ms': round(read_time * 1000, 2),
            'data_integrity': retrieved_data == test_data,
        })
        
        # Clean up
        cache.delete(test_key)
        
        return cache_stats

    def analyze_database(self):
        """Analyze database performance"""
        # Get basic database stats
        db_stats = get_database_stats()
        
        # Test database performance
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        query_time = time.time() - start_time
        
        db_stats.update({
            'connection_test_ms': round(query_time * 1000, 2),
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'database_name': settings.DATABASES['default'].get('NAME', 'Unknown'),
        })
        
        # Check for common performance issues
        issues = []
        
        # Check if DEBUG is enabled in production
        if not settings.DEBUG and hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES['default']
            if 'CONN_MAX_AGE' not in db_config or db_config.get('CONN_MAX_AGE', 0) == 0:
                issues.append("Database connection pooling is not enabled (CONN_MAX_AGE)")
        
        # Check for slow queries
        if 'slow_queries' in db_stats and db_stats['slow_queries']:
            issues.append(f"Found {len(db_stats['slow_queries'])} slow queries (>100ms)")
        
        db_stats['performance_issues'] = issues
        
        return db_stats

    def display_console_results(self, results):
        """Display results in console format"""
        if 'models' in results:
            self.stdout.write(self.style.SUCCESS('\n=== MODEL ANALYSIS ==='))
            for model_name, analysis in results['models'].items():
                self.stdout.write(f"\n{model_name}:")
                for suggestion in analysis['suggestions']:
                    self.stdout.write(f"  • {suggestion}")
                
                if analysis['foreign_keys']:
                    self.stdout.write(f"  Foreign keys: {', '.join(analysis['foreign_keys'])}")
                
                if analysis['indexed_fields']:
                    self.stdout.write(f"  Indexed fields: {', '.join(analysis['indexed_fields'])}")
        
        if 'cache' in results:
            self.stdout.write(self.style.SUCCESS('\n=== CACHE ANALYSIS ==='))
            cache_stats = results['cache']
            self.stdout.write(f"Backend: {cache_stats['backend']}")
            self.stdout.write(f"Location: {cache_stats['location']}")
            self.stdout.write(f"Write performance: {cache_stats['write_time_ms']}ms")
            self.stdout.write(f"Read performance: {cache_stats['read_time_ms']}ms")
            self.stdout.write(f"Data integrity: {'✓' if cache_stats['data_integrity'] else '✗'}")
        
        if 'database' in results:
            self.stdout.write(self.style.SUCCESS('\n=== DATABASE ANALYSIS ==='))
            db_stats = results['database']
            self.stdout.write(f"Engine: {db_stats['database_engine']}")
            self.stdout.write(f"Connection test: {db_stats['connection_test_ms']}ms")
            self.stdout.write(f"Total queries in session: {db_stats['total_queries']}")
            
            if 'avg_time' in db_stats:
                self.stdout.write(f"Average query time: {db_stats['avg_time']:.3f}s")
                self.stdout.write(f"Max query time: {db_stats['max_time']:.3f}s")
            
            if db_stats.get('performance_issues'):
                self.stdout.write(self.style.WARNING('\nPerformance Issues:'))
                for issue in db_stats['performance_issues']:
                    self.stdout.write(f"  ⚠ {issue}")
        
        # General recommendations
        self.stdout.write(self.style.SUCCESS('\n=== GENERAL RECOMMENDATIONS ==='))
        recommendations = [
            "Enable Redis caching for production",
            "Use select_related() and prefetch_related() for foreign key queries",
            "Add database indexes for frequently filtered fields",
            "Enable connection pooling (CONN_MAX_AGE)",
            "Use django-debug-toolbar in development to identify slow queries",
            "Consider using django-silk for production query monitoring",
            "Implement view-level caching for expensive operations",
            "Use pagination for large querysets",
            "Consider database read replicas for read-heavy workloads",
            "Enable static file compression and CDN for production"
        ]
        
        for rec in recommendations:
            self.stdout.write(f"  • {rec}")
        
        self.stdout.write(self.style.SUCCESS('\nAnalysis complete!'))