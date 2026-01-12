import google.generativeai as genai
from app.utils.config import GEMINI_API_KEY
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response dari Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
