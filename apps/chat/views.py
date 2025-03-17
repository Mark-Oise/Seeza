from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import Conversation, Message
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from collections import defaultdict
from django.core.files.storage import default_storage

def conversation_list(request):
    """
    View function to display a grouped and paginated list of conversations.
    """
    search_query = request.GET.get('search', '')
    
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(
            user=request.user,
            is_deleted=False
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        conversations = Conversation.objects.filter(
            session_key=session_key,
            is_deleted=False
        )
    
    if search_query:
        conversations = conversations.filter(title__icontains=search_query)
    
    conversations = conversations.order_by('-updated_at')

    paginator = Paginator(conversations, 10)  # Show 10 conversations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Group conversations
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    last_week = today - timezone.timedelta(days=7)

    grouped_conversations = defaultdict(list)

    for conversation in page_obj:
        if conversation.updated_at.date() == today:
            grouped_conversations['Today'].append(conversation)
        elif conversation.updated_at.date() == yesterday:
            grouped_conversations['Yesterday'].append(conversation)
        elif conversation.updated_at.date() > last_week:
            grouped_conversations['Last 7 days'].append(conversation)
        else:
            grouped_conversations['Older'].append(conversation)

    return render(request, 'chat/partials/conversation_list.html', {
        'grouped_conversations': dict(grouped_conversations),
        'page_obj': page_obj,
        'search_query': search_query
    })


def home(request):
    """
    View function for the home page.
    Clear temp_images from session on page load.
    """
    # Clear temp images on page load
    if 'temp_images' in request.session:
        # Clean up any temp files stored
        for image_data in request.session.get('temp_images', []):
            if 'path' in image_data:
                default_storage.delete(image_data['path'])
        # Remove from session
        request.session.pop('temp_images', None)
        request.session.modified = True
    
    return render(request, 'chat/home.html')


def create_conversation(request):
    """
    View function to create a new conversation.
    Expects a POST request with a 'message' parameter.
    """
    if request.method == 'POST':
        message = request.POST.get('message')
        initial_title = "New Conversation"

        if request.user.is_authenticated:
            conversation = Conversation.objects.create(user=request.user, title=initial_title)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            conversation = Conversation.objects.create(session_key=session_key, title=initial_title)

        # Create user message
        user_message = Message.objects.create(conversation=conversation, sender='user', content=message)
        
        # Process any attached images
        temp_images = request.session.get('temp_images', [])
        if temp_images:
            from .services.image_service import ImageService
            image_service = ImageService()
            # Use synchronous version since we're in a view
            image_service.attach_temp_images_to_message_sync(user_message, temp_images)
            
            # Clear temp images from session
            request.session.pop('temp_images', None)
            request.session.modified = True

    return redirect(reverse('chat:conversation_detail', kwargs={'slug': conversation.slug}))


def conversation_detail(request, slug):
    """
    View function to display details of a specific conversation.
    Clear temp_images from session on page load.
    """
    conversation = get_object_or_404(Conversation, slug=slug)
    if request.user.is_authenticated:
        if conversation.user != request.user:
            return redirect('chat:home')
    else:
        if conversation.session_key != request.session.session_key:
            return redirect('chat:home')

    # Clear temp images on page load
    if 'temp_images' in request.session:
        # Clean up any temp files stored
        for image_data in request.session.get('temp_images', []):
            if 'path' in image_data:
                default_storage.delete(image_data['path'])
        # Remove from session
        request.session.pop('temp_images', None)
        request.session.modified = True

    # Fetch messages in the correct order, avoiding duplicates
    messages = conversation.messages.order_by('created_at').distinct()
    

    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'is_conversation_detail': True,
        'is_starred': conversation.is_starred,  
    })


def get_conversation_title(request, slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    response = HttpResponse(conversation.title)
    
    # Only trigger the event if the title is no longer "New Conversation"
    if conversation.title != "New Conversation":
        response['HX-Trigger'] = 'titleFetched'
    
    return response