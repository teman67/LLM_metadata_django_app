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
            ('llama3.3:70b-instruct-q8_0', 'llama3.3:70b instruct'),
            ('qwen3:32b-q8_0', 'qwen3:32b'),
            ('phi4-reasoning:14b-plus-fp16', 'phi4-reasoning:14b'),
            # ('llama3.1:latest', 'Llama 3.1'),
            # ('llama3.3:latest', 'Llama 3.3'),
            # ('mixtral:latest', 'Mixtral'),
            # ('deepseek-v2:latest', 'DeepSeek v2 16b'),
            # ('nemotron:latest', 'Nemotron'),
            # ('mistral-large:latest', 'Mistral Large'),
            # ('deepseek-coder:6.7b', 'DeepSeek Coder 6.7b'),
            # ('deepseek-r1:70b', 'DeepSeek r1 70b'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Model"
    )
    max_tokens = forms.IntegerField(
        initial=600,
        min_value=1,
        max_value=3000,
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
        max_value=100,
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
    
    def clean_max_tokens(self):
        max_tokens = self.cleaned_data['max_tokens']
        if not (1 <= max_tokens <= 3000):
            raise forms.ValidationError("Max tokens must be between 1 and 3000.")
        return max_tokens

    def clean_temperature(self):
        temperature = self.cleaned_data['temperature']
        if not (0 <= temperature <= 1):
            raise forms.ValidationError("Temperature must be between 0 and 1.")
        return temperature

    def clean_top_p(self):
        top_p = self.cleaned_data['top_p']
        if not (0 <= top_p <= 1):
            raise forms.ValidationError("Top-p must be between 0 and 1.")
        return top_p

    def clean_top_k(self):
        top_k = self.cleaned_data['top_k']
        if not (0 <= top_k <= 100):
            raise forms.ValidationError("Top-k must be between 0 and 100.")
        return top_k
