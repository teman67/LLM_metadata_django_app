"""
Tests for API rate limiting and caching functionality
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from LLM_Metadata.models import Conversation
import uuid
from django.utils import timezone


class RateLimitingTests(TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        cache.clear()
    
    def test_health_check_endpoint_exists(self):
        """Test that health check endpoint is accessible"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
    
    def test_api_health_check_endpoint_exists(self):
        """Test that API health check endpoint is accessible"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')


class CachingTests(TestCase):
    """Test caching functionality"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create some test conversations
        for i in range(3):
            Conversation.objects.create(
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Test content {i}',
                username=self.user.username,
                conversation_id=uuid.uuid4(),
                timestamp=timezone.now()
            )
        
        cache.clear()
    
    def test_conversation_stats_caching(self):
        """Test that conversation stats are cached"""
        # First request - not cached
        response1 = self.client.get('/api/conversations/stats/')
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertFalse(data1.get('cached', True))
        
        # Second request - should be cached
        response2 = self.client.get('/api/conversations/stats/')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertTrue(data2.get('cached', False))
        
        # Data should be the same
        self.assertEqual(data1['total_conversations'], data2['total_conversations'])
    
    def test_cache_invalidation_on_delete(self):
        """Test that cache is invalidated when conversation is deleted"""
        # Get initial stats (creates cache)
        response1 = self.client.get('/api/conversations/stats/')
        data1 = response1.json()
        initial_count = data1['total_conversations']
        
        # Delete a conversation
        conversation = Conversation.objects.filter(username=self.user.username).first()
        response = self.client.delete(
            f'/api/conversations/{conversation.conversation_id}/'
        )
        self.assertEqual(response.status_code, 200)
        
        # Get stats again - cache should be invalidated
        response2 = self.client.get('/api/conversations/stats/')
        data2 = response2.json()
        self.assertFalse(data2.get('cached', True))
        self.assertLess(data2['total_conversations'], initial_count)


class APIEndpointsTests(TestCase):
    """Test API endpoints functionality"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.conversation_id = uuid.uuid4()
        
        # Create test conversations
        Conversation.objects.create(
            role='user',
            content='Test question',
            username=self.user.username,
            conversation_id=self.conversation_id,
            timestamp=timezone.now()
        )
        Conversation.objects.create(
            role='assistant',
            content='Test response',
            username=self.user.username,
            conversation_id=self.conversation_id,
            timestamp=timezone.now()
        )
        
        cache.clear()
    
    def test_conversation_stats_requires_authentication(self):
        """Test that conversation stats endpoint requires authentication"""
        response = self.client.get('/api/conversations/stats/')
        self.assertEqual(response.status_code, 401)
    
    def test_conversation_stats_returns_correct_data(self):
        """Test that conversation stats returns correct data"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/conversations/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['user'], 'testuser')
        self.assertEqual(data['total_conversations'], 2)
        self.assertIsInstance(data['recent_conversations'], list)
    
    def test_delete_conversation_api(self):
        """Test deleting conversation via API"""
        self.client.login(username='testuser', password='testpass123')
        
        # Delete conversation
        response = self.client.delete(
            f'/api/conversations/{self.conversation_id}/'
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['conversation_id'], str(self.conversation_id))
        
        # Verify conversations are deleted
        remaining = Conversation.objects.filter(
            conversation_id=self.conversation_id
        ).count()
        self.assertEqual(remaining, 0)
    
    def test_delete_nonexistent_conversation(self):
        """Test deleting a conversation that doesn't exist"""
        self.client.login(username='testuser', password='testpass123')
        
        fake_uuid = uuid.uuid4()
        response = self.client.delete(f'/api/conversations/{fake_uuid}/')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_conversation_requires_authentication(self):
        """Test that delete requires authentication"""
        response = self.client.delete(
            f'/api/conversations/{self.conversation_id}/'
        )
        self.assertEqual(response.status_code, 401)


class SettingsTests(TestCase):
    """Test that settings are configured correctly"""
    
    def test_rest_framework_configured(self):
        """Test that REST framework is configured"""
        from django.conf import settings
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('DEFAULT_THROTTLE_CLASSES', settings.REST_FRAMEWORK)
    
    def test_cache_configured(self):
        """Test that cache is configured"""
        from django.conf import settings
        self.assertIn('default', settings.CACHES)
        self.assertIn('BACKEND', settings.CACHES['default'])
    
    def test_ratelimit_configured(self):
        """Test that rate limiting is configured"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'RATELIMIT_ENABLE'))
        self.assertTrue(hasattr(settings, 'RATELIMIT_USE_CACHE'))
