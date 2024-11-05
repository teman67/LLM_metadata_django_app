from django import forms
from .models import Conversation
from django.core.exceptions import ValidationError

class ConversationForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your question here...'}))

    class Meta:
        model = Conversation
        fields = ['content']


class QuestionForm(forms.Form):
    question = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type your question here...'}),
        label="Your Question"
    )
    model = forms.ChoiceField(
        choices=[
            ('mixtral:latest', 'Mixtral'),
            ('nemotron:latest', 'Nemotron'),
            ('mistral-large:latest', 'Mistral Large'),
            ('llama3.1:latest', 'Llama 3.1')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Model"
    )
    max_tokens = forms.IntegerField(
        initial=600,
        min_value=1,
        label="Max Tokens",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    temperature = forms.FloatField(
        initial=0.7,
        min_value=0,
        max_value=1,
        label="Temperature",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    top_k = forms.IntegerField(
        initial=40,
        min_value=0,
        label="Top K",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    top_p = forms.FloatField(
        initial=0.9,
        min_value=0,
        max_value=1,
        label="Top P",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    file_upload = forms.FileField(required=False)

    def clean_file_upload(self):
        file = self.cleaned_data.get('file_upload')
        if file:
            # Check the file size (limit to 30 MB)
            if file.size > 30 * 1024 * 1024:  # 30 MB
                raise ValidationError("File size must not exceed 30 MB.")

            # Check the file type (only allow .txt, .doc, .json, .csv)
            valid_extensions = ['.txt', '.doc', '.json', '.csv']
            ext = file.name.split('.')[-1].lower()
            if f'.{ext}' not in valid_extensions:
                raise ValidationError(f"Unsupported file type: {ext}. Allowed types are: {', '.join(valid_extensions)}.")

        return file