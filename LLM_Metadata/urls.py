from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('conversation/', views.conversation_view, name='conversation'),
]