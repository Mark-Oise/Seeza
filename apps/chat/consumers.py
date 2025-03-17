import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .services.ai_service import GeminiService
from .services.message_service import MessageService
from .services.ui_service import UIService
from .services.image_service import ImageService

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat with AI.
    
    Handles connections, message processing, and AI response generation
    using the Gemini model from Google's Generative AI.
    """

    async def connect(self):
        """Establish WebSocket connection and initialize the chat session."""
        self.conversation_slug = self.scope['url_route']['kwargs']['conversation_slug']
        self.room_group_name = f'chat_{self.conversation_slug}'

        # Get the user or session key
        self.user = self.scope['user']
        self.session_key = self.scope['session'].session_key

        # Initialize services
        self.ai_service = GeminiService()
        self.message_service = MessageService(
            self.conversation_slug,
            user=self.user,
            session_key=self.session_key
        )
        self.ui_service = UIService(self, self.room_group_name)
        self.image_service = ImageService()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Initialize Gemini model
        await self.ai_service.initialize()
        
        # Load conversation and check for pending messages
        self.conversation_history = await self.message_service.load_conversation_history()
        await self.check_initial_message()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket."""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.ui_service.send_loading_button()
        user_message = await self.message_service.save_message('user', message)

        # Process any attached images
        temp_images = self.scope['session'].get('temp_images', [])
        image_attachments = []
        
        if temp_images:
            # Attach temporary images to the message
            image_attachments = await self.image_service.attach_temp_images_to_message(user_message, temp_images)
            
            # Clear temp images from session
            self.scope['session'].pop('temp_images', None)
            self.scope['session'].modified = True

        # Add user message to conversation history
        self.conversation_history.append({'role': 'user', 'parts': [message]})

        # Render and send user message to all in the group
        await self.ui_service.send_rendered_message(user_message, 'chat/partials/user_message.html', 
                                                  {'image_attachments': image_attachments})

        # Send typing indicator
        await self.ui_service.send_typing_indicator()

        # Process AI response asynchronously
        asyncio.create_task(self.process_ai_response(image_attachments))

    async def process_ai_response(self, image_attachments=None):
        """Process and stream AI response to the user."""
        # Generate AI response using Gemini
        response = await self.ai_service.generate_response(self.conversation_history, image_attachments)

        # Save initial empty AI message
        bot_message = await self.message_service.save_message('bot', '')

        # Remove typing indicator
        await self.ui_service.remove_typing_indicator()

        # Send initial empty bot message
        await self.ui_service.send_initial_bot_message(bot_message)

        # Stream the response
        full_response = await self.stream_ai_response(bot_message, response)

        # Generate title if this is the first message
        if len(self.conversation_history) == 2:  # User message + AI response
            title = await self.ai_service.generate_title(
                self.conversation_history[0]['parts'][0], 
                full_response
            )
            await self.message_service.update_conversation_title(title)

        # Swap back to submit button
        await self.ui_service.send_submit_button()

    async def stream_ai_response(self, bot_message, response):
        """Stream the AI response to the client, updating in chunks."""
        full_response = ""
        buffer = ""
        buffer_size = 30  
        
        for chunk in response:
            if chunk.text:
                buffer += chunk.text
                
                # Only update when buffer reaches certain size or it's the last chunk
                if len(buffer) >= buffer_size:
                    full_response += buffer
                    await self.message_service.update_message(bot_message, full_response)
                    await self.ui_service.update_message_content(bot_message, full_response)
                    buffer = ""
                    
        # Send any remaining buffer content
        if buffer:
            full_response += buffer
            await self.message_service.update_message(bot_message, full_response)
            await self.ui_service.update_message_content(bot_message, full_response)

        # Update the full message in the database
        full_response = full_response.strip()
        await self.message_service.update_message(bot_message, full_response)

        # Add bot response to conversation history
        self.conversation_history.append({'role': 'model', 'parts': [full_response]})

        return full_response

    async def chat_message(self, event):
        """Send message to WebSocket."""
        message_html = event['message']
        await self.send(text_data=message_html)
        
    async def check_initial_message(self):
        """Check if there's an initial message that needs a response."""
        initial_message = await self.message_service.get_initial_message()
        has_response = await self.message_service.has_bot_response()
        
        if initial_message and not has_response:
            # Get any image attachments
            image_attachments = await self.message_service.get_message_attachments(initial_message.id)
            
            # Swap to loading button
            await self.ui_service.send_typing_indicator()
            await self.ui_service.send_loading_button()
            asyncio.create_task(self.process_ai_response(image_attachments))


    