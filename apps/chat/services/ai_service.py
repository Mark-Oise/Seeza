import environ
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from channels.db import database_sync_to_async
import base64
from PIL import Image
import io

env = environ.Env()
environ.Env.read_env()

class GeminiService:
    """Service for interacting with Google's Gemini AI model."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        self.model = None
        self.vision_model = None
    
    async def initialize(self):
        """Initialize the Gemini AI model."""
        google_api_key = env("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a helpful AI assistant. Provide accurate and helpful responses. "
                              "Eliminate Emoji's from your responses and maintain a general, friendly tone, "
                              "remove any mention of your name and only respond with the text of your response."
        )
        # Initialize vision model
        self.vision_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a helpful AI assistant that can analyze images. "
                              "Provide accurate, clear, and concise descriptions. "
                              "Eliminate Emoji's from your responses and maintain a general, friendly tone."
        )
    
    async def generate_response(self, conversation_history, image_attachments=None):
        """Generate a response from the AI model."""
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=1000,
            temperature=0.7,
            top_p=0.8,
            top_k=40,
        )
        
        # If there are images, use vision model with images and text
        if image_attachments and len(image_attachments) > 0:
            content_parts = []
            
            # Add previous conversation context if available (excluding the last user message)
            if len(conversation_history) > 1:
                prior_context = conversation_history[:-1]
                for message in prior_context:
                    content_parts.append({"role": message["role"], "parts": [{"text": message["parts"][0]}]})
            
            # Get the user's current message
            user_message = conversation_history[-1]["parts"][0] if conversation_history else ""
            
            # Add images followed by the user's message
            image_parts = []
            for attachment in image_attachments:
                image_bytes = await database_sync_to_async(self._get_image_bytes)(attachment.image)
                image_parts.append({"inline_data": {"mime_type": self._get_mime_type(attachment.image.name), "data": base64.b64encode(image_bytes).decode("utf-8")}})
            
            # Add user's message and images to the content parts
            content_parts.append({
                "role": "user", 
                "parts": image_parts + [{"text": user_message or "What can you tell me about these images?"}]
            })
            
            return await database_sync_to_async(self.vision_model.generate_content)(
                content_parts,
                generation_config=generation_config,
                stream=True,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
        
        # Otherwise, use regular text model
        return await database_sync_to_async(self.model.generate_content)(
            conversation_history,
            generation_config=generation_config,
            stream=True,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
    
    def _get_image_bytes(self, image_field):
        """Get the bytes from an image field."""
        image_field.open()
        image_bytes = image_field.read()
        image_field.close()
        return image_bytes
    
    def _get_mime_type(self, filename):
        """Determine the MIME type based on file extension."""
        extension = filename.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp',
            'heic': 'image/heic',
            'heif': 'image/heif',
        }
        return mime_types.get(extension, 'image/jpeg')
    
    async def generate_title(self, user_message, ai_response):
        """Generate a title for the conversation."""
        title_prompt = f"Based on this conversation, generate a short, concise title (max 5 words):\nUser: {user_message}\nAI: {ai_response}"
        
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

        return title_response.text.strip()