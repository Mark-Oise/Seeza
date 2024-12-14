from .models import Conversation
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.template.defaultfilters import truncatechars
from django.contrib.auth.decorators import login_required


@require_POST
def rename_conversation(request, slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    new_title = request.POST.get('title')
    
    if new_title:
        conversation.rename_title(new_title)
        
    return HttpResponse(truncatechars(conversation.title, 25))

# class archive_conversation(request):
#     pass

@login_required
@require_POST
def star_conversation(request, slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    is_starred = conversation.toggle_star()
    return render(request, 'chat/partials/buttons/star_button.html', {
        'is_starred': is_starred,
        'conversation': conversation
    })

@require_POST
def delete_conversation(request, slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    
    # Check if the user has permission to delete the conversation
    if request.user.is_authenticated:
        if conversation.user != request.user:
            messages.error(request, "You don't have permission to delete this conversation.")
            return redirect('chat:home')
    else:
        if conversation.session_key != request.session.session_key:
            messages.error(request, "You don't have permission to delete this conversation.")
            return redirect('chat:home')
    
    conversation.delete()
    messages.success(request, "Conversation deleted successfully.")
    return redirect('chat:home')