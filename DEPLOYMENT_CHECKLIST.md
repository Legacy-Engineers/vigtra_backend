# Production Deployment Checklist - Performance Optimizations

## Pre-Deployment Performance Setup

### ✅ Database Optimization
- [ ] Configure connection pooling (`CONN_MAX_AGE = 3600`)
- [ ] Set up read replica if needed
- [ ] Enable database query logging for monitoring
- [ ] Run database migrations with indexes
- [ ] Configure database connection limits

### ✅ Cache Configuration
- [ ] Set up Redis cluster for production
- [ ] Configure cache backend (`CACHE_BACKEND=redis`)
- [ ] Set appropriate cache timeouts
- [ ] Test cache connectivity
- [ ] Configure cache monitoring

### ✅ Static Files & CDN
- [ ] Build and compress static files (`npm run build`)
- [ ] Configure CDN for static file delivery
- [ ] Set up proper cache headers
- [ ] Enable GZip compression on web server
- [ ] Test static file serving

### ✅ Environment Variables
```bash
# Required production environment variables
export DJANGO_ENV=production
export DEBUG=False
export CACHE_BACKEND=redis
export CACHE_URL=redis://your-redis-host:6379/1
export DB_ENGINE=postgresql
export DB_HOST=your-db-host
export DB_NAME=vigtra_prod
export DB_USER=vigtra_user
export DB_PASSWORD=secure_password
export DJANGO_SECRET=your-secure-secret-key
export ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### ✅ Web Server Configuration

#### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json image/svg+xml;
    
    # Static files with long cache
    location /static/ {
        alias /path/to/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /path/to/media/;
        expires 30d;
    }
    
    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### ✅ Performance Monitoring Setup
- [ ] Configure application performance monitoring (APM)
- [ ] Set up log aggregation
- [ ] Configure error tracking
- [ ] Set up performance alerts
- [ ] Configure database monitoring

## Deployment Steps

### 1. Pre-deployment Testing
```bash
# Run performance analysis
python manage.py performance_analysis --all --output file

# Run database optimization checks
python manage.py performance_analysis --database

# Test cache connectivity
python manage.py performance_analysis --cache

# Build frontend assets
npm run build

# Run tests
python manage.py test
```

### 2. Database Migration
```bash
# Backup production database
pg_dump vigtra_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
python manage.py migrate

# Create cache table if using database cache
python manage.py createcachetable
```

### 3. Static Files Collection
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify static files are compressed
ls -la staticfiles/
```

### 4. Cache Warming (Optional)
```bash
# Warm up critical caches
python manage.py shell -c "
from vigtra.utils.db_optimization import warm_cache
warm_cache()
"
```

## Post-Deployment Verification

### ✅ Performance Checks
- [ ] Verify page load times (< 2 seconds)
- [ ] Check database query counts (< 30 per request)
- [ ] Verify cache hit rates (> 80%)
- [ ] Test static file loading speeds
- [ ] Verify CDN is serving static files

### ✅ Monitoring Setup
- [ ] Check performance monitoring dashboard
- [ ] Verify error tracking is working
- [ ] Test performance alerts
- [ ] Check log aggregation
- [ ] Monitor database performance

### ✅ Load Testing
```bash
# Basic load test
ab -n 1000 -c 10 https://your-domain.com/

# API endpoint testing
ab -n 500 -c 5 https://your-domain.com/api/users/

# Static file testing
ab -n 1000 -c 20 https://your-domain.com/static/css/main.css
```

## Performance Benchmarks

### Target Metrics
- **Page Load Time**: < 2 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 3 seconds
- **Database Queries**: < 30 per request
- **Cache Hit Rate**: > 80%
- **Server Response Time**: < 200ms

### Monitoring Commands
```bash
# Check current performance
python manage.py performance_analysis --all

# Monitor database queries
python manage.py performance_analysis --database

# Check cache performance
python manage.py performance_analysis --cache

# View performance logs
tail -f logs/vigtra.log | grep -E "(Slow request|Cache hit rate|DB queries)"
```

## Rollback Plan

### If Performance Issues Occur
1. **Immediate Actions**:
   ```bash
   # Disable performance middleware temporarily
   export PERFORMANCE_MONITORING=False
   
   # Switch to dummy cache if Redis issues
   export CACHE_BACKEND=dummy
   
   # Restart application servers
   systemctl restart gunicorn
   ```

2. **Database Issues**:
   ```bash
   # Restore from backup if needed
   psql vigtra_prod < backup_YYYYMMDD_HHMMSS.sql
   
   # Disable connection pooling temporarily
   export CONN_MAX_AGE=0
   ```

3. **Static File Issues**:
   ```bash
   # Serve static files directly from Django (temporary)
   export DEBUG=True  # Only for static files debugging
   ```

## Ongoing Maintenance

### Daily Checks
- [ ] Monitor performance dashboard
- [ ] Check error logs for performance issues
- [ ] Verify cache hit rates
- [ ] Monitor database performance

### Weekly Tasks
- [ ] Run performance analysis report
- [ ] Review slow query logs
- [ ] Check static file CDN performance
- [ ] Monitor memory usage trends

### Monthly Reviews
- [ ] Analyze performance trends
- [ ] Review and optimize slow endpoints
- [ ] Update cache strategies based on usage
- [ ] Plan capacity upgrades if needed

## Performance Alert Thresholds

### Critical Alerts
- Page load time > 5 seconds
- Database queries > 100 per request
- Cache hit rate < 50%
- Server response time > 1 second
- Memory usage > 90%

### Warning Alerts
- Page load time > 3 seconds
- Database queries > 50 per request
- Cache hit rate < 70%
- Server response time > 500ms
- Memory usage > 80%

## Contact Information

For performance issues or questions:
- **Development Team**: dev-team@vigtra.com
- **DevOps Team**: devops@vigtra.com
- **Emergency Contact**: +1-XXX-XXX-XXXX

---

*This checklist ensures optimal performance for the Vigtra healthcare management system in production.*