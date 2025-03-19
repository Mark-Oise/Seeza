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
from .services.image_service import ImageService


def clear_temp_images(request):
    """Clear temporary images from the session."""
    if 'temp_images' in request.session:
        for image_data in request.session.get('temp_images', []):
            if 'path' in image_data:
                default_storage.delete(image_data['path'])
        request.session.pop('temp_images', None)
        request.session.modified = True


def process_message_images(request, message):
    """Process and attach any temporary images to a message."""
    temp_images = request.session.get('temp_images', [])
    if temp_images:
        image_service = ImageService()
        image_service.attach_temp_images_to_message_sync(message, temp_images)
        request.session.pop('temp_images', None)
        request.session.modified = True


def conversation_list(request):
    """
    View function to display a grouped and paginated list of conversations.
    """
    search_query = request.GET.get('search', '')
    
    # Get conversations for authenticated user or session
    conversations = get_user_conversations(request)
    
    # Apply search filter if query exists
    if search_query:
        conversations = conversations.filter(title__icontains=search_query)
    
    conversations = conversations.order_by('-updated_at')

    # Paginate results
    page_obj = paginate_conversations(conversations, request.GET.get('page'))

    # Group conversations by time period
    grouped_conversations = group_conversations_by_date(page_obj)

    return render(request, 'chat/partials/conversation_list.html', {
        'grouped_conversations': dict(grouped_conversations),
        'page_obj': page_obj,
        'search_query': search_query
    })


def get_user_conversations(request):
    """Get conversations for authenticated user or session."""
    if request.user.is_authenticated:
        return Conversation.objects.filter(user=request.user, is_deleted=False)
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return Conversation.objects.filter(session_key=session_key, is_deleted=False)


def paginate_conversations(conversations, page_number):
    """Paginate conversations list."""
    paginator = Paginator(conversations, 10)  # Show 10 conversations per page
    return paginator.get_page(page_number)


def group_conversations_by_date(conversations):
    """Group conversations by time period."""
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1) 
    last_week = today - timezone.timedelta(days=7)

    grouped = defaultdict(list)
    
    for conversation in conversations:
        conversation_date = conversation.updated_at.date()
        if conversation_date == today:
            grouped['Today'].append(conversation)
        elif conversation_date == yesterday:
            grouped['Yesterday'].append(conversation)
        elif conversation_date > last_week:
            grouped['Last 7 days'].append(conversation)
        else:
            grouped['Older'].append(conversation)
            
    return grouped


def home(request):
    """View function for the home page."""
    clear_temp_images(request)
    return render(request, 'chat/home.html')


def create_conversation(request):
    """Create a new conversation."""
    if request.method == 'POST':
        message = request.POST.get('message')
        initial_title = "New Conversation"

        # Create conversation
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
        
        # Process attached images
        process_message_images(request, user_message)

    return redirect(reverse('chat:conversation_detail', kwargs={'slug': conversation.slug}))


def conversation_detail(request, slug):
    """Display conversation details."""
    conversation = get_object_or_404(Conversation, slug=slug)
    
    # Validate access permission
    if request.user.is_authenticated:
        if conversation.user != request.user:
            return redirect('chat:home')
    else:
        if conversation.session_key != request.session.session_key:
            return redirect('chat:home')

    clear_temp_images(request)
    
    # Fetch messages
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