import environ
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from channels.db import database_sync_to_async

env = environ.Env()
environ.Env.read_env()

class GeminiService:
    """Service for interacting with Google's Gemini AI model."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        self.model = None
    
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
    
    async def generate_response(self, conversation_history):
        """Generate a response from the AI model."""
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=1000,
            temperature=0.7,
            top_p=0.8,
            top_k=40,
        )
        
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