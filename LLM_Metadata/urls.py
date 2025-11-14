from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.home, name='home'),
    path('conversation/', views.conversation_view, name='conversation'),
    # path('delete_conversation/<uuid:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('ask/', views.ask_question_view, name='ask_question'),
    path('json-viewer/', views.json_viewer, name='json_viewer'),
    path('delete_conversation/<int:user_convo_id>/', views.delete_conversation, name='delete_conversation'),
    path('health/', views.health_check, name='health_check'),
    
    # API endpoints with rate limiting and caching
    path('api/health/', api.api_health_check, name='api_health_check'),
    path('api/conversations/stats/', api.api_conversation_stats, name='api_conversation_stats'),
    path('api/conversations/<uuid:conversation_id>/', api.api_delete_conversation, name='api_delete_conversation'),
]
