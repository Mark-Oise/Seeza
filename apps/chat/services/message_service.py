from channels.db import database_sync_to_async
from ..models import Conversation, Message, ImageAttachment

class MessageService:
    """Service for database operations related to messages and conversations."""
    
    def __init__(self, conversation_slug, user=None, session_key=None):
        """Initialize the message service."""
        self.conversation_slug = conversation_slug
        self.user = user
        self.session_key = session_key
        
    @database_sync_to_async
    def save_message(self, sender, content):
        """Save a message to the database."""
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        if self.user and self.user.is_authenticated:
            conversation.user = self.user
        elif self.session_key:
            conversation.session_key = self.session_key
        conversation.save()
        return Message.objects.create(conversation=conversation, sender=sender, content=content)

    @database_sync_to_async
    def update_message(self, message, content):
        """Update message content in the database."""
        message.content = content
        message.save()
        return message

    @database_sync_to_async
    def update_conversation_title(self, title):
        """Update the conversation title in the database."""
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        conversation.title = title
        conversation.save()

    @database_sync_to_async
    def load_conversation_history(self):
        """Load conversation history from the database."""
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        messages = conversation.messages.order_by('created_at')
        history = []
        for msg in messages:
            history.append({
                'role': 'user' if msg.sender == 'user' else 'model',
                'parts': [msg.content]
            })
        return history

    @database_sync_to_async
    def get_initial_message(self):
        """Get the first user message in the conversation."""
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        return conversation.messages.filter(sender='user').order_by('created_at').first()

    @database_sync_to_async
    def has_bot_response(self):
        """Check if there's a bot response in the conversation."""
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        return conversation.messages.filter(sender='bot').exists()

    @database_sync_to_async
    def get_message_attachments(self, message_id):
        """Get all image attachments for a message."""
        return list(ImageAttachment.objects.filter(message_id=message_id))