from django import template
from LLM_Metadata.models import Conversation

register = template.Library()

@register.filter
def get_assistant_for_user(conversation_id):
    return Conversation.objects.filter(conversation_id=conversation_id, role='assistant').first()