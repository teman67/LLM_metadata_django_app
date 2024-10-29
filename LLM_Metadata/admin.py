from django.contrib import admin
from .models import Conversation

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'content', 'model_name', 'token_usage', 'elapsed_time', 'timestamp', 'username', 'conversation_id')
    list_filter = ('role', 'model_name', 'timestamp')
    search_fields = ('content', 'username__username')
    ordering = ('-timestamp',)

admin.site.register(Conversation, ConversationAdmin)