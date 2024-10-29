from django import forms
from .models import Conversation

class ConversationForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your question here...'}))

    class Meta:
        model = Conversation
        fields = ['content']
