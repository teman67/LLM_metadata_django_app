# API Rate Limiting and Caching Implementation

This document describes the rate limiting and caching implementation for the LLM Metadata Django App API.

## Overview

The application now includes:
1. **Rate Limiting** - Controls the number of requests users can make to API endpoints
2. **Caching** - Stores frequently accessed data to improve performance
3. **REST API Endpoints** - Clean API endpoints with proper throttling and caching

## Features Implemented

### 1. Rate Limiting

Rate limiting is implemented using two approaches:

#### A. Django REST Framework Throttling
Configured in `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
    }
}
```

#### B. Django-Ratelimit Decorators
Applied to individual views:
- `ask_question_view`: 50 requests/hour per user
- `conversation_view`: 100 requests/hour per user
- `health_check`: 200 requests/hour per IP
- `json_viewer`: 50 requests/hour per IP
- `delete_conversation`: 30 requests/hour per user

### 2. Caching Configuration

Two caching backends are supported:

#### A. Local Memory Cache (Default for Development)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

#### B. Redis Cache (Recommended for Production)
Uncomment and configure in `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'TIMEOUT': 300,
    }
}
```

### 3. API Endpoints

New REST API endpoints in `LLM_Metadata/api.py`:

#### `/api/health/`
- **Method**: GET
- **Rate Limit**: 200 requests/hour (IP-based)
- **Cache**: 1 minute
- **Description**: Health check endpoint with database connectivity test
- **Response**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "database": {
      "total_conversations": 100,
      "latest_conversation_date": "2024-01-01T00:00:00Z"
    },
    "message": "API is operational"
  }
  ```

#### `/api/conversations/stats/`
- **Method**: GET
- **Rate Limit**: 50 requests/hour (user-based)
- **Cache**: 5 minutes (per user)
- **Authentication**: Required
- **Description**: Returns conversation statistics for the authenticated user
- **Response**:
  ```json
  {
    "user": "username",
    "total_conversations": 50,
    "recent_conversations": [...],
    "cached": false
  }
  ```

#### `/api/conversations/<uuid:conversation_id>/`
- **Method**: DELETE
- **Rate Limit**: 50 requests/hour (user-based)
- **Authentication**: Required
- **Description**: Deletes a conversation by UUID
- **Response**:
  ```json
  {
    "message": "Successfully deleted 2 conversation entries",
    "conversation_id": "uuid-here"
  }
  ```

## Rate Limiting Details

### Per-Endpoint Limits

| Endpoint | Method | Rate Limit | Key |
|----------|--------|-----------|-----|
| `/ask/` | POST | 50/hour | User |
| `/conversation/` | POST | 100/hour | User |
| `/health/` | GET/POST | 200/hour | IP |
| `/json-viewer/` | POST | 50/hour | IP |
| `/delete_conversation/<id>/` | POST | 30/hour | User |
| `/api/health/` | GET | 200/hour | IP |
| `/api/conversations/stats/` | GET | 50/hour | User |
| `/api/conversations/<uuid>/` | DELETE | 50/hour | User |

### Rate Limit Responses

When a rate limit is exceeded, the user receives a 429 Too Many Requests response:
```json
{
    "detail": "Request was throttled. Expected available in X seconds."
}
```

## Caching Strategy

### Cached Data

1. **Health Check Endpoint**: Cached for 1 minute to reduce database load
2. **Conversation Statistics**: Cached for 5 minutes per user
3. **Cache Invalidation**: Automatically invalidated when:
   - User creates a new conversation
   - User deletes a conversation

### Cache Keys

- Health check: Based on URL
- User stats: `conversation_stats_{user_id}`

## Configuration

### Environment Variables

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: (Optional) Redis connection string for caching

### Enable/Disable Rate Limiting

To disable rate limiting (e.g., in development):
```python
# In settings.py
RATELIMIT_ENABLE = False
```

## Testing

### Test Rate Limiting

1. Make multiple rapid requests to an endpoint:
   ```bash
   for i in {1..60}; do
     curl -X POST http://localhost:8000/ask/ \
       -H "Authorization: Bearer <token>" \
       -d "question=test"
   done
   ```

2. After 50 requests, you should receive a 429 response

### Test Caching

1. First request to `/api/conversations/stats/`:
   - Response includes `"cached": false`
   - Query time: ~100ms

2. Subsequent requests within 5 minutes:
   - Response includes `"cached": true`
   - Query time: ~5ms

## Production Deployment

### Using Redis (Recommended)

1. Install Redis:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. Update `settings.py`:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
       }
   }
   ```

3. Set environment variable:
   ```bash
   export REDIS_URL='redis://your-redis-host:6379/1'
   ```

### Monitoring

Monitor rate limiting and caching:
```python
from django.core.cache import cache

# Check cache statistics
cache_keys = cache.keys('*')  # Redis only
print(f"Total cached items: {len(cache_keys)}")
```

## Dependencies

New dependencies added (see `requirements_api.txt`):
- `djangorestframework==3.16.1` - REST API framework
- `django-ratelimit==4.1.0` - Rate limiting decorator
- `redis==7.0.1` - Redis client (optional, for production caching)

## Security Considerations

1. **Rate Limiting**: Protects against:
   - DDoS attacks
   - Brute force attempts
   - API abuse

2. **Caching**: 
   - User-specific data is cached with user-specific keys
   - Cache invalidation ensures data consistency
   - Sensitive data is not cached

3. **Authentication**:
   - API endpoints require authentication where appropriate
   - Anonymous users have stricter rate limits

## Future Enhancements

1. **Dynamic Rate Limits**: Adjust limits based on user tier/subscription
2. **Cache Warming**: Pre-populate cache with frequently accessed data
3. **Rate Limit Analytics**: Track and analyze rate limit hits
4. **Custom Throttle Classes**: Create more sophisticated throttling strategies
5. **CDN Integration**: Integrate with CDN for static asset caching

## Troubleshooting

### Rate Limit Not Working
- Check `RATELIMIT_ENABLE = True` in settings
- Verify decorators are properly applied to views
- Check cache backend is working

### Cache Not Working
- Verify cache backend configuration
- Check Redis connection (if using Redis)
- Clear cache: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

### 429 Too Many Requests
- Wait for the rate limit window to reset
- Check rate limit configuration
- Contact administrator to increase limits if needed

## References

- [Django REST Framework Throttling](https://www.django-rest-framework.org/api-guide/throttling/)
- [Django Caching Documentation](https://docs.djangoproject.com/en/4.2/topics/cache/)
- [django-ratelimit Documentation](https://django-ratelimit.readthedocs.io/)
