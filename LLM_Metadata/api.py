"""
API views using Django REST Framework with rate limiting and caching
"""
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Conversation
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
import uuid
from django.utils import timezone


class ConversationRateThrottle(UserRateThrottle):
    """Custom throttle for conversation API - 50 requests per hour"""
    rate = '50/hour'


class HealthCheckRateThrottle(AnonRateThrottle):
    """Custom throttle for health check API - 200 requests per hour"""
    rate = '200/hour'


@api_view(['GET'])
@throttle_classes([HealthCheckRateThrottle])
@cache_page(60)  # Cache for 1 minute
def api_health_check(request):
    """
    API endpoint for health check with rate limiting and caching
    Returns system health status
    """
    try:
        # Test database connection
        total_conversations = Conversation.objects.count()
        latest_conversation = Conversation.objects.first()
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': {
                'total_conversations': total_conversations,
                'latest_conversation_date': latest_conversation.timestamp.isoformat() if latest_conversation else None,
            },
            'message': 'API is operational'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
            'message': 'Database connection failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@throttle_classes([ConversationRateThrottle])
def api_conversation_stats(request):
    """
    API endpoint to get conversation statistics with caching
    Returns user's conversation count and recent activity
    """
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Try to get cached data first
    cache_key = f'conversation_stats_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        cached_data['cached'] = True
        return Response(cached_data, status=status.HTTP_200_OK)
    
    # If not cached, query database
    user_conversations = Conversation.objects.filter(username=request.user.username)
    total_count = user_conversations.count()
    recent_conversations = user_conversations.order_by('-timestamp')[:5]
    
    data = {
        'user': request.user.username,
        'total_conversations': total_count,
        'recent_conversations': [
            {
                'id': conv.id,
                'role': conv.role,
                'content': conv.content[:100] + '...' if len(conv.content) > 100 else conv.content,
                'timestamp': conv.timestamp.isoformat(),
                'model_name': conv.model_name,
            }
            for conv in recent_conversations
        ],
        'cached': False
    }
    
    # Cache the data for 5 minutes
    cache.set(cache_key, data, 300)
    
    return Response(data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@throttle_classes([ConversationRateThrottle])
def api_delete_conversation(request, conversation_id):
    """
    API endpoint to delete a conversation with rate limiting
    """
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get conversations with this conversation_id belonging to the user
        conversations = Conversation.objects.filter(
            conversation_id=conversation_id,
            username=request.user.username
        )
        
        if not conversations.exists():
            return Response({
                'error': 'Conversation not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        count = conversations.count()
        conversations.delete()
        
        # Invalidate cache for this user's stats
        cache_key = f'conversation_stats_{request.user.id}'
        cache.delete(cache_key)
        
        return Response({
            'message': f'Successfully deleted {count} conversation entries',
            'conversation_id': str(conversation_id)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
