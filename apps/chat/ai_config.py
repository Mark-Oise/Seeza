from django.conf import settings
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import environ

env = environ.Env()
environ.Env.read_env()


google_api_key = env("GOOGLE_API_KEY")
        


def initialize_genai():
    """Initialize and configure the Gemini AI model."""
    genai.configure(api_key=google_api_key)
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are a helpful AI assistant. Provide accurate and helpful responses. "
            "Eliminate Emoji's from your responses and maintain a general, friendly tone, "
            "remove any mention of your name and only respond with the text of your response."
        )
    )
    
    return model


def get_generation_config(mode='standard'):
    """Get generation configuration based on mode."""
    configs = {
        'standard': {
            'candidate_count': 1,
            'max_output_tokens': 1000,
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
        },
        'title': {
            'candidate_count': 1,
            'max_output_tokens': 10,
            'temperature': 0.2,
            'top_p': 1,
            'top_k': 1,
        }
    }
    return genai.types.GenerationConfig(**configs[mode])


def get_safety_settings():
    """Get default safety settings."""
    return {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }