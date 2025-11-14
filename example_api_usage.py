#!/usr/bin/env python3
"""
Example script demonstrating how to use the LLM Metadata Django App API
with rate limiting and caching.

This script shows how to:
1. Check API health
2. Get conversation statistics
3. Handle rate limiting
4. Utilize caching

Prerequisites:
- pip install requests
- Django server running locally or on production
"""

import requests
import time
import json
from typing import Dict, Optional


class LLMMetadataClient:
    """Client for interacting with the LLM Metadata API"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API (e.g., 'http://localhost:8000')
            auth_token: Optional authentication token for authenticated endpoints
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def health_check(self) -> Dict:
        """
        Check API health status
        
        Returns:
            Dictionary containing health status
            
        Rate limit: 200 requests/hour per IP
        Cached: 1 minute
        """
        url = f'{self.base_url}/api/health/'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_conversation_stats(self) -> Dict:
        """
        Get conversation statistics for the authenticated user
        
        Returns:
            Dictionary containing conversation statistics
            
        Rate limit: 50 requests/hour per user
        Cached: 5 minutes per user
        Requires: Authentication
        """
        url = f'{self.base_url}/api/conversations/stats/'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def delete_conversation(self, conversation_id: str) -> Dict:
        """
        Delete a conversation by UUID
        
        Args:
            conversation_id: UUID of the conversation to delete
            
        Returns:
            Dictionary containing deletion confirmation
            
        Rate limit: 50 requests/hour per user
        Requires: Authentication
        """
        url = f'{self.base_url}/api/conversations/{conversation_id}/'
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()


def demonstrate_health_check(client: LLMMetadataClient):
    """Demonstrate health check endpoint with caching"""
    print("\n" + "="*60)
    print("1. HEALTH CHECK DEMONSTRATION")
    print("="*60)
    
    # First request - not cached
    print("\n📡 Making first health check request...")
    start_time = time.time()
    health = client.health_check()
    first_request_time = time.time() - start_time
    
    print(f"✓ Status: {health['status']}")
    print(f"✓ Response time: {first_request_time*1000:.2f}ms")
    print(f"✓ Total conversations: {health['database']['total_conversations']}")
    
    # Second request - cached (within 1 minute)
    print("\n📡 Making second health check request (should be cached)...")
    start_time = time.time()
    health = client.health_check()
    cached_request_time = time.time() - start_time
    
    print(f"✓ Status: {health['status']}")
    print(f"✓ Response time: {cached_request_time*1000:.2f}ms")
    
    speedup = first_request_time / cached_request_time if cached_request_time > 0 else 0
    print(f"\n⚡ Cache speedup: {speedup:.2f}x faster")


def demonstrate_conversation_stats(client: LLMMetadataClient):
    """Demonstrate conversation statistics with caching"""
    print("\n" + "="*60)
    print("2. CONVERSATION STATISTICS DEMONSTRATION")
    print("="*60)
    
    # First request - not cached
    print("\n📊 Fetching conversation statistics...")
    start_time = time.time()
    stats = client.get_conversation_stats()
    first_request_time = time.time() - start_time
    
    print(f"✓ User: {stats['user']}")
    print(f"✓ Total conversations: {stats['total_conversations']}")
    print(f"✓ Recent conversations: {len(stats['recent_conversations'])}")
    print(f"✓ Cached: {stats.get('cached', False)}")
    print(f"✓ Response time: {first_request_time*1000:.2f}ms")
    
    # Second request - cached
    print("\n📊 Fetching conversation statistics again (should be cached)...")
    start_time = time.time()
    stats = client.get_conversation_stats()
    cached_request_time = time.time() - start_time
    
    print(f"✓ User: {stats['user']}")
    print(f"✓ Cached: {stats.get('cached', False)}")
    print(f"✓ Response time: {cached_request_time*1000:.2f}ms")
    
    speedup = first_request_time / cached_request_time if cached_request_time > 0 else 0
    print(f"\n⚡ Cache speedup: {speedup:.2f}x faster")


def demonstrate_rate_limiting(client: LLMMetadataClient):
    """Demonstrate rate limiting by making multiple requests"""
    print("\n" + "="*60)
    print("3. RATE LIMITING DEMONSTRATION")
    print("="*60)
    
    print("\n⏱️  Making rapid requests to test rate limiting...")
    print("(This will stop when rate limit is reached)")
    
    for i in range(1, 11):
        try:
            health = client.health_check()
            print(f"✓ Request {i}: Success (status: {health['status']})")
            time.sleep(0.1)  # Small delay between requests
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"\n⚠️  Rate limit reached at request {i}!")
                print(f"   HTTP 429: Too Many Requests")
                try:
                    error_data = e.response.json()
                    print(f"   Message: {error_data.get('detail', 'Rate limit exceeded')}")
                except:
                    pass
                break
            else:
                raise


def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("LLM METADATA API DEMONSTRATION")
    print("Rate Limiting and Caching Features")
    print("="*60)
    
    # Configuration
    BASE_URL = "http://localhost:8000"  # Change to your server URL
    AUTH_TOKEN = None  # Set this if you have an auth token
    
    print(f"\n📍 API Base URL: {BASE_URL}")
    print(f"🔐 Authentication: {'Enabled' if AUTH_TOKEN else 'Disabled (using anonymous access)'}")
    
    # Create client
    client = LLMMetadataClient(BASE_URL, AUTH_TOKEN)
    
    try:
        # 1. Demonstrate health check with caching
        demonstrate_health_check(client)
        
        # 2. Demonstrate conversation stats (requires authentication)
        if AUTH_TOKEN:
            demonstrate_conversation_stats(client)
        else:
            print("\n" + "="*60)
            print("2. CONVERSATION STATISTICS DEMONSTRATION")
            print("="*60)
            print("\n⚠️  Skipped: Requires authentication")
            print("   Set AUTH_TOKEN to enable this demonstration")
        
        # 3. Demonstrate rate limiting
        demonstrate_rate_limiting(client)
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*60)
        print("\nKey Takeaways:")
        print("1. ⚡ Caching significantly improves response times")
        print("2. 🛡️  Rate limiting protects the API from abuse")
        print("3. 🔒 Sensitive endpoints require authentication")
        print("4. 📊 Statistics are cached per user for 5 minutes")
        print("\nFor more information, see RATE_LIMITING_AND_CACHING.md")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to {BASE_URL}")
        print("   Make sure the Django server is running")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("   Authentication required. Set AUTH_TOKEN in the script.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
