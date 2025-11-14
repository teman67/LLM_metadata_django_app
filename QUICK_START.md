# Quick Start Guide: Rate Limiting and Caching

This guide will help you quickly get started with the rate limiting and caching features.

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install djangorestframework==3.16.1 django-ratelimit==4.1.0 redis==7.0.1
```

Or install from the requirements file:
```bash
pip install -r requirements_api.txt
```

### Step 2: Verify Configuration

The configuration is already set up in `main/settings.py`. No changes needed for local development!

✅ Cache backend: Local memory (default)
✅ Rate limiting: Enabled
✅ REST Framework: Configured

### Step 3: Run Migrations

```bash
python manage.py migrate
```

### Step 4: Start the Server

```bash
python manage.py runserver
```

### Step 5: Test the API

Open a new terminal and run:
```bash
python example_api_usage.py
```

You should see:
```
✓ Health check working
✓ Caching enabled (faster responses)
✓ Rate limiting active (protects from abuse)
```

## 📊 Available Endpoints

### 1. Health Check (Public)
```bash
curl http://localhost:8000/api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "database": {
    "total_conversations": 100
  }
}
```

**Features:**
- Rate limit: 200 requests/hour per IP
- Cached for 1 minute
- No authentication required

### 2. Conversation Statistics (Authenticated)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/conversations/stats/
```

**Response:**
```json
{
  "user": "username",
  "total_conversations": 50,
  "recent_conversations": [...],
  "cached": false
}
```

**Features:**
- Rate limit: 50 requests/hour per user
- Cached for 5 minutes per user
- Requires authentication

### 3. Delete Conversation (Authenticated)
```bash
curl -X DELETE \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/conversations/<uuid>/
```

**Features:**
- Rate limit: 50 requests/hour per user
- Invalidates cache automatically
- Requires authentication

## 🧪 Testing

Run the test suite:
```bash
python manage.py test LLM_Metadata.test_api
```

Expected output:
```
Ran 12 tests in 3.0s
OK
```

## 🔒 Rate Limit Examples

### Example 1: Normal Usage
```python
import requests

# First 50 requests work fine
for i in range(50):
    response = requests.get('http://localhost:8000/api/health/')
    print(f"Request {i+1}: {response.status_code}")
```

### Example 2: Rate Limit Exceeded
```python
# After 200 requests in an hour:
response = requests.get('http://localhost:8000/api/health/')
# Status: 429 Too Many Requests
```

## ⚡ Caching Examples

### Example 1: First Request (Not Cached)
```python
import requests
import time

start = time.time()
response = requests.get('http://localhost:8000/api/health/')
duration = time.time() - start
print(f"First request: {duration*1000:.2f}ms")
# Output: ~100ms
```

### Example 2: Second Request (Cached)
```python
start = time.time()
response = requests.get('http://localhost:8000/api/health/')
duration = time.time() - start
print(f"Cached request: {duration*1000:.2f}ms")
# Output: ~5ms (20x faster!)
```

## 🌍 Production Setup

### For Heroku with Redis

1. Add Redis addon:
```bash
heroku addons:create heroku-redis:mini
```

2. Update `settings.py` (uncomment Redis configuration):
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

3. Deploy:
```bash
git push heroku main
```

### Environment Variables

Required in production:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
REDIS_URL=redis://your-redis-host:6379/1  # Optional, for Redis cache
```

## 📈 Monitoring

### Check Cache Statistics

```python
from django.core.cache import cache

# Get a cached value
stats = cache.get('conversation_stats_1')

# Clear cache
cache.clear()

# Set custom cache
cache.set('my_key', 'my_value', timeout=300)
```

### Monitor Rate Limits

Check server logs for rate limit hits:
```bash
tail -f logs/django.log | grep "rate limit"
```

## 🛠️ Customization

### Adjust Rate Limits

Edit `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/hour',  # Change this
        'user': '2000/hour',  # Change this
    }
}
```

### Adjust Cache Timeout

Edit `settings.py`:
```python
CACHES = {
    'default': {
        'TIMEOUT': 600,  # 10 minutes instead of 5
    }
}
```

### Disable Rate Limiting (Development Only)

Edit `settings.py`:
```python
RATELIMIT_ENABLE = False  # Disable for testing
```

## 🔍 Troubleshooting

### Issue: "Too Many Requests" Error

**Solution:** Wait for the rate limit window to reset (1 hour) or increase limits in settings.

### Issue: Cache Not Working

**Check:**
1. Is cache backend configured correctly?
2. Is Redis running (if using Redis)?
3. Clear cache: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

### Issue: Slow Responses Even with Cache

**Check:**
1. Verify cache is being used (check `cached` field in response)
2. Check Redis connection (if using Redis)
3. Monitor database queries with Django Debug Toolbar

## 📚 Next Steps

1. Read full documentation: `RATE_LIMITING_AND_CACHING.md`
2. Explore the API in your browser: http://localhost:8000/api/
3. Integrate with your frontend application
4. Set up Redis for production
5. Monitor and optimize based on usage patterns

## 💡 Tips

1. **Use caching for read-heavy endpoints** - Statistics, dashboards, reports
2. **Invalidate cache on writes** - Update, create, delete operations
3. **Set appropriate TTLs** - Balance freshness vs performance
4. **Monitor rate limits** - Adjust based on actual usage patterns
5. **Use Redis in production** - Much better than local memory cache

## 🆘 Getting Help

- 📖 Full documentation: `RATE_LIMITING_AND_CACHING.md`
- 🧪 Test examples: `LLM_Metadata/test_api.py`
- 💻 Usage examples: `example_api_usage.py`
- 📧 Support: amirhossein.bayani@gmail.com

---

**You're all set! The API is now protected with rate limiting and optimized with caching. 🎉**
