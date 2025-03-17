import json
from channels.db import database_sync_to_async
from django.template.loader import render_to_string


class UIService:
    """Service for handling UI updates and messaging."""
    
    def __init__(self, consumer, room_group_name):
        """Initialize the UI service."""
        self.consumer = consumer
        self.room_group_name = room_group_name
        
    async def send_typing_indicator(self):
        """Send typing indicator to the client."""
        typing_html = await self.render_partial('chat/partials/loading_message.html')
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{typing_html}</div>',
            }
        )

    async def remove_typing_indicator(self):
        """Remove typing indicator from the client."""
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': '<div id="loading-message" hx-swap-oob="delete"></div>',
            }
        )

    async def send_loading_button(self):
        """Send loading button to the client."""
        loading_html = await self.render_partial('chat/partials/buttons/loading_button.html')
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="button-container" hx-swap-oob="innerHTML">{loading_html}</div>',
            }
        )

    async def send_submit_button(self):
        """Send submit button to the client."""
        submit_html = await self.render_partial('chat/partials/buttons/submit_button.html')
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="button-container" hx-swap-oob="innerHTML">{submit_html}</div>',
            }
        )

    async def send_initial_bot_message(self, bot_message):
        """Send initial empty bot message to the client."""
        initial_message = await self.render_message(
            {'content': '', 'id': bot_message.id},
            'chat/partials/bot_message.html'
        )
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{initial_message}</div>',
            }
        )

    async def send_rendered_message(self, message, template_name, extra_context=None):
        """Send a rendered message to all clients in the group."""
        rendered_message = await self.render_message(message, template_name, extra_context)
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{rendered_message}</div>',
            }
        )
        
    async def update_message_content(self, bot_message, content):
        """Update message content on the client."""
        rendered_content = await database_sync_to_async(bot_message.get_content_as_markdown)()
        await self.consumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-content-{bot_message.id}" hx-swap-oob="innerHTML">{rendered_content}</div>',
            }
        )
    
    @database_sync_to_async
    def render_message(self, message, template_name, extra_context=None):
        """Render a message using a template."""
        context = {'message': message}
        if extra_context:
            context.update(extra_context)
        return render_to_string(template_name, context)

    @database_sync_to_async
    def render_partial(self, template_name, context=None):
        """Render a partial template."""
        return render_to_string(template_name, context or {})