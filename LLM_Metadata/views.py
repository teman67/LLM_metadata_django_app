from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Conversation
from .forms import ConversationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import uuid
# myapp/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Conversation
from django.utils import timezone
import os
import requests
import uuid
from .utils import query_api  # Assuming query_api is refactored to a helper function

def home(request):
    if request.method == "POST":
        # Handle submission for user questions
        user_question = request.POST.get("user_question")
        selected_model = request.POST.get("selected_model", "mixtral:latest")
        language = request.POST.get("language", "English")
        conversation_id = uuid.uuid4()

        # Prepare API messages and query the model
        api_messages = [{"role": "user", "content": user_question}]
        result = query_api(api_messages, selected_model)

        if "error" in result:
            return JsonResponse({"error": result['error']})

        # Save both user message and response to the database
        user_msg = Conversation.objects.create(
            role="user", content=user_question, username=request.user.username, conversation_id=conversation_id
        )
        response = Conversation.objects.create(
            role="assistant", content=result["content"], model_name=selected_model, token_usage=result["response_tokens"],
            elapsed_time=result["elapsed_time"], username=request.user.username, conversation_id=conversation_id
        )

        return JsonResponse({
            "response": result["content"],
            "elapsed_time": result["elapsed_time"],
            "tokens": result["response_tokens"]
        })

    # Display the form with any previous conversation history
    conversations = Conversation.objects.filter(username=request.user.username)
    return render(request, 'home.html', {'conversations': conversations})


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
    return render(request, 'conversation.html', {'form': form, 'conversations': conversations})


# class Home(TemplateView):
#     template_name = 'home.html'