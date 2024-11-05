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

    # Pair user and assistant messages
    paired_conversations = []
    for i in range(0, len(conversations) - 1, 2):
        user_convo = conversations[i + 1] if (i + 1) < len(conversations) else None
        ai_convo = conversations[i]
        paired_conversations.append((user_convo, ai_convo))

    return render(request, 'LLM_Metadata/conversation.html', {'form': form, 'paired_conversations': paired_conversations})


@login_required
def ask_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if form.is_valid():
            question = form.cleaned_data['question']
            model = form.cleaned_data['model']
            max_tokens = form.cleaned_data['max_tokens']
            temperature = form.cleaned_data['temperature']
            top_k = form.cleaned_data['top_k']
            top_p = form.cleaned_data['top_p']
            file_upload = form.cleaned_data.get('file_upload')  # Get the uploaded file if available
            
            # Retrieve or generate a conversation ID
            conversation_id = request.session.get('current_conversation_id', None)
            if not conversation_id:
                conversation_id = uuid.uuid4()
                request.session['current_conversation_id'] = str(conversation_id)

            # Fetch previous conversation history
            previous_conversations = Conversation.objects.filter(
                conversation_id=conversation_id
            ).order_by('timestamp')

            # Format history for the API
            api_messages = [
                {"role": conv.role, "content": conv.content}
                for conv in previous_conversations
            ]
            # Add the new user question to the messages list
            api_messages.append({"role": "user", "content": question})

            # Handle file upload (if necessary)
            file_content = ''
            if file_upload:
                file_content = file_upload.read().decode('utf-8')  # Decode the byte content to a string
                # Optionally, add additional formatting/cleaning here

            # Include the uploaded file content in the messages
            if file_content:
                api_messages.append({"role": "user", "content": f"Here is some additional context from the uploaded file: {file_content}"})

            try:
                # Query the API with the conversation history
                response = query_api(api_messages, model, temperature, max_tokens, top_k, top_p)

                if 'error' not in response:
                    # Save the user question
                    user_conversation = Conversation.objects.create(
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
                    
                    # Save the AI response
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
                        top_p=top_p,
                    )
                    
                else:
                    error_message = mark_safe(
                        f"An error occurred while contacting the model: Please contact <a href='mailto:amirhossein.bayani@gmail.com'>admin</a>"
                    )
                    django_messages.error(request, error_message)

            except Exception as e:
                error_message = mark_safe(
                    f"An error occurred while contacting the model: Please contact <a href='mailto:amirhossein.bayani@gmail.com'>admin</a>"
                )
                django_messages.error(request, error_message)

    else:
        form = QuestionForm()

    # Retrieve all messages in the current conversation
    conversation_id = request.session.get('current_conversation_id')
    if conversation_id:
        conversations = Conversation.objects.filter(conversation_id=conversation_id)
    else:
        conversations = []

    # Pair user and assistant messages
    paired_conversations = []
    for i in range(0, len(conversations) - 1, 2):
        user_convo = conversations[i + 1] if (i + 1) < len(conversations) else None
        ai_convo = conversations[i]
        paired_conversations.append((user_convo, ai_convo))

    return render(request, 'LLM_Metadata/ask_question.html', {
        'form': form,
        'conversations': conversations,
        'paired_conversations': paired_conversations  # Pass the paired conversations to the template
    })


