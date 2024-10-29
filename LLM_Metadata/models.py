# myapp/models.py
from django.db import models
from django.utils import timezone
import uuid

class Conversation(models.Model):
    """
    Represents a conversation message stored in the database.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    model_name = models.CharField(max_length=100, null=True, blank=True)
    token_usage = models.IntegerField(null=True, blank=True)
    elapsed_time = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=100)
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        db_table = 'conversations'
        ordering = ['-timestamp']
