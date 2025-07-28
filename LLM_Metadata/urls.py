from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('conversation/', views.conversation_view, name='conversation'),
    # path('delete_conversation/<uuid:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('ask/', views.ask_question_view, name='ask_question'),
    path('json-viewer/', views.json_viewer, name='json_viewer'),
        path('delete_conversation/<int:user_convo_id>/', views.delete_conversation, name='delete_conversation'),
    path('health/', views.health_check, name='health_check'),
]
