from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Conversation
from .forms import ConversationForm, QuestionForm
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation
from django.utils import timezone
from .utils import query_api 
import uuid
from django.contrib import messages as django_messages 



def home(request):
    return render(request, 'home.html')


@login_required
def conversation_view(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.role = 'user'
            conversation.username = request.user
            conversation.conversation_id = uuid.uuid4()
            conversation.timestamp = timezone.now()
            conversation.save()

            # Add AI response
            response_content = "Simulated AI response to: " + conversation.content  # Replace with actual API call
            Conversation.objects.create(
                role='assistant',
                content=response_content,
                model_name='Selected Model',
                username=request.user,
                conversation_id=conversation.conversation_id,
                timestamp=timezone.now()
            )
            return redirect('conversation')

    else:
        form = ConversationForm()
    
    conversations = Conversation.objects.filter(username=request.user).order_by('-timestamp')
    return render(request, 'LLM_Metadata/conversation.html', {'form': form, 'conversations': conversations})


@login_required
def ask_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            model = form.cleaned_data['model']
            max_tokens = form.cleaned_data['max_tokens']
            temperature = form.cleaned_data['temperature']
            top_k = form.cleaned_data['top_k']
            top_p = form.cleaned_data['top_p']

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
        conversations = Conversation.objects.filter(conversation_id=conversation_id).order_by('timestamp')
    else:
        conversations = []

    return render(request, 'LLM_Metadata/ask_question.html', {'form': form, 'conversations': conversations})

