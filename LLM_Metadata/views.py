from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Conversation
from .forms import ConversationForm, QuestionForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation
from django.utils import timezone
from django.contrib import messages as django_messages
from django.utils.safestring import mark_safe
from .utils import query_api  # Assuming query_api is refactored to a helper function
import uuid
from collections import defaultdict
import json

def home(request):
    
    return render(request, 'home.html')


@login_required
def conversation_view(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.role = 'user'
            conversation.username = request.user  # Use User instance
            conversation.conversation_id = uuid.uuid4()  # Unique per conversation
            conversation.timestamp = timezone.now()
            conversation.save()

            # Simulated AI response (Replace with actual API call)
            response_content = "Simulated AI response to: " + conversation.content
            Conversation.objects.create(
                role='assistant',
                content=response_content,
                model_name='Selected Model',
                username=request.user,  # Use User instance
                conversation_id=conversation.conversation_id,
                timestamp=timezone.now()
            )
            return redirect('conversation')

    else:
        form = ConversationForm()

    # Fetch conversations for the logged-in user, newest first
    conversations = Conversation.objects.filter(username=request.user).order_by('-timestamp')

    # Group conversations by date
    grouped_conversations = defaultdict(list)
    for i in range(0, len(conversations) - 1, 2):
        user_convo = conversations[i + 1] if (i + 1) < len(conversations) else None
        ai_convo = conversations[i]
        convo_date = ai_convo.timestamp.date()  # Group by date of the assistant's response
        grouped_conversations[convo_date].append((user_convo, ai_convo))

    # Convert defaultdict to a sorted dictionary (sorted by date)
    grouped_conversations = dict(sorted(grouped_conversations.items(), reverse=True))

    return render(request, 'LLM_Metadata/conversation.html', {
        'form': form,
        'grouped_conversations': grouped_conversations
    })


@login_required
def ask_question_view(request):
    # Only clear the conversation when a fresh GET request is made (i.e., the user is revisiting)
    if request.method == 'GET':
        request.session.pop('current_conversation_id', None)

    form = QuestionForm(request.POST or None, request.FILES or None)  # Simplify form instantiation
    if request.method == 'POST' and form.is_valid():
        question = form.cleaned_data['question']
        model = form.cleaned_data['model']
        max_tokens = form.cleaned_data['max_tokens']
        temperature = form.cleaned_data['temperature']
        top_k = form.cleaned_data['top_k']
        top_p = form.cleaned_data['top_p']
        file_upload = form.cleaned_data.get('file_upload')

        # Generate or get a conversation ID
        conversation_id = request.session.get('current_conversation_id')
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            request.session['current_conversation_id'] = conversation_id

        # Build conversation history for the API
        previous_conversations = Conversation.objects.filter(
            conversation_id=conversation_id
        ).order_by('timestamp')

        api_messages = [{"role": conv.role, "content": conv.content} for conv in previous_conversations]
        api_messages.append({"role": "user", "content": question})

        file_content = ''
        if file_upload:
            file_content = file_upload.read().decode('utf-8')
            api_messages.append({"role": "user", "content": f"Here is some additional context from the uploaded file: {file_content}"})

        try:
            response = query_api(api_messages, model, temperature, max_tokens, top_k, top_p)
            if 'error' not in response:
                # Save user question
                Conversation.objects.create(
                    role='user',
                    content=question,
                    username=request.user.username,
                    conversation_id=conversation_id,
                    timestamp=timezone.now(),
                    model_name=model,
                    token_usage=response['response_tokens'],
                    elapsed_time=round(response['elapsed_time'], 2),
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    file_upload=file_upload
                )
                # Save AI response
                Conversation.objects.create(
                    role='assistant',
                    content=response['content'],
                    username=request.user.username,
                    conversation_id=conversation_id,
                    timestamp=timezone.now(),
                    model_name=model,
                    token_usage=response['response_tokens'],
                    elapsed_time=round(response['elapsed_time'], 2),
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p
                )
            else:
                django_messages.error(request, "An error occurred while contacting the model. Please try again or contact support.")

        except Exception as e:
            django_messages.error(request, "An error occurred while contacting the model. Please try again or contact support.")

    # Get the conversation for the current session ID
    conversation_id = request.session.get('current_conversation_id')
    conversations = Conversation.objects.filter(conversation_id=conversation_id) if conversation_id else []

    # Pair user and assistant messages
    paired_conversations = [
        (conversations[i + 1] if (i + 1) < len(conversations) else None, conversations[i])
        for i in range(0, len(conversations) - 1, 2)
    ]

    return render(request, 'LLM_Metadata/ask_question.html', {
        'form': form,
        'conversations': conversations,
        'paired_conversations': paired_conversations
    })


def json_viewer(request):
    context = {}

    if request.method == "POST" and request.FILES.get("jsonFile"):
        json_file = request.FILES["jsonFile"]

        try:
            json_data = json.load(json_file)

            # Render JSON as a raw display
            context['json_data'] = json.dumps(json_data, indent=4)

            # Check if JSON data is a list of dictionaries to display as a table
            if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                context['is_table'] = True
                context['table_data'] = json_data

        except json.JSONDecodeError:
            context['error'] = "Invalid JSON file. Please upload a valid JSON file."

    return render(request, 'LLM_Metadata/json_viewer.html', context)