import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from .models import Conversation, Message
import google.generativeai as genai
import environ

env = environ.Env()
environ.Env.read_env()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_slug = self.scope['url_route']['kwargs']['conversation_slug']
        self.room_group_name = f'chat_{self.conversation_slug}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        google_api_key = env("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a helpful AI assistant. Provide accurate and helpful responses. Eliminate Emoji's from your responses and maintain a general, friendly tone, remove any mention of your name and only respond with the text of your response."
        )

        self.conversation_history = []
        await self.load_conversation_history()
        await self.check_initial_message()

        self.user = self.scope['user']
        self.session_key = self.scope['session'].session_key

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send_loading_button()

        user_message = await self.save_message('user', message)
        self.conversation_history.append({'role': 'user', 'parts': [message]})

        await self.send_rendered_message(user_message, 'chat/partials/user_message.html')
        await self.send_typing_indicator()
        asyncio.create_task(self.process_ai_response())

    async def process_ai_response(self):
        response = await self.generate_ai_response()

        bot_message = await self.save_message('bot', '')
        await self.remove_typing_indicator()
        await self.send_initial_bot_message(bot_message)

        full_response = await self.stream_ai_response(bot_message, response)

        if len(self.conversation_history) == 2:  # User message + AI response
            await self.generate_title(full_response)

        await self.send_submit_button()

    async def generate_ai_response(self):
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=1000,
            temperature=0.7,
            top_p=0.8,
            top_k=40,
        )

        return await database_sync_to_async(self.model.generate_content)(
            self.conversation_history,
            generation_config=generation_config,
            stream=True,
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        )

    async def stream_ai_response(self, bot_message, response):
        full_response = ""
        for chunk in response:
            if chunk.text:
                for char in chunk.text:
                    full_response += char
                    await self.update_message(bot_message, full_response)
                    rendered_content = await database_sync_to_async(bot_message.get_content_as_markdown)()
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': f'<div id="message-content-{bot_message.id}" hx-swap-oob="innerHTML">{rendered_content}</div>',
                        }
                    )
                    await asyncio.sleep(0.001)

        await self.update_message(bot_message, full_response.strip())
        self.conversation_history.append({'role': 'model', 'parts': [full_response.strip()]})

        return full_response.strip()

    async def generate_title(self, ai_response):
        title_prompt = f"Based on this conversation, generate a short, concise title (max 5 words):\nUser: {self.conversation_history[0]['parts'][0]}\nAI: {ai_response}"

        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=10,
            temperature=0.2,
            top_p=1,
            top_k=1,
        )

        title_response = await database_sync_to_async(self.model.generate_content)(
            title_prompt,
            generation_config=generation_config,
        )

        title = title_response.text.strip()
        await self.update_conversation_title(title)

    @database_sync_to_async
    def update_conversation_title(self, title):
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        conversation.title = title
        conversation.save()

    async def send_typing_indicator(self):
        typing_html = await self.render_message(None, 'chat/partials/loading_message.html')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{typing_html}</div>',
            }
        )

    async def remove_typing_indicator(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': '<div id="loading-message" hx-swap-oob="delete"></div>',
            }
        )

    async def send_button_swap(self, template_name):
        rendered_button = await self.render_partial(template_name)
        await self.send(text_data=json.dumps({
            'type': 'swap_button',
            'html': rendered_button
        }))

    async def send_initial_bot_message(self, bot_message):
        initial_message = await self.render_message(
            {'content': '', 'id': bot_message.id},
            'chat/partials/bot_message.html'
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{initial_message}</div>',
            }
        )

    async def send_rendered_message(self, message, template_name):
        rendered_message = await self.render_message(message, template_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="message-list" hx-swap-oob="beforeend">{rendered_message}</div>',
            }
        )

    async def chat_message(self, event):
        message_html = event['message']
        await self.send(text_data=message_html)

    @database_sync_to_async
    def save_message(self, sender, content):
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        if self.user.is_authenticated:
            conversation.user = self.user
        else:
            conversation.session_key = self.session_key
        conversation.save()
        return Message.objects.create(conversation=conversation, sender=sender, content=content)

    @database_sync_to_async
    def update_message(self, message, content):
        message.content = content
        message.save()
        return message

    @database_sync_to_async
    def render_message(self, message, template_name):
        return render_to_string(template_name, {'message': message})

    @database_sync_to_async
    def render_partial(self, template_name):
        return render_to_string(template_name)

    @database_sync_to_async
    def load_conversation_history(self):
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        messages = conversation.messages.order_by('created_at')
        for msg in messages:
            self.conversation_history.append({
                'role': 'user' if msg.sender == 'user' else 'model',
                'parts': [msg.content]
            })

    @database_sync_to_async
    def get_initial_message(self):
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        return conversation.messages.filter(sender='user').order_by('created_at').first()

    @database_sync_to_async
    def has_bot_response(self):
        conversation = Conversation.objects.get(slug=self.conversation_slug)
        return conversation.messages.filter(sender='bot').exists()

    async def check_initial_message(self):
        initial_message = await self.get_initial_message()
        has_response = await self.has_bot_response()

        if initial_message and not has_response:
            await self.send_typing_indicator()
            await self.send_loading_button()
            asyncio.create_task(self.process_ai_response())

    async def send_loading_button(self):
        loading_html = await self.render_message(None, 'chat/partials/buttons/loading_button.html')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="button-container" hx-swap-oob="innerHTML">{loading_html}</div>',
            }
        )

    async def send_submit_button(self):
        submit_html = await self.render_message(None, 'chat/partials/buttons/submit_button.html')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="button-container" hx-swap-oob="innerHTML">{submit_html}</div>',
            }
        )

    async def button_group(self, message_id):
        button_group_html = await self.render_message(None, 'chat/partials/buttons/button_group.html')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'<div id="button-group-container" hx-swap-oob="innerHTML">{button_group_html}</div>',
            }
        )