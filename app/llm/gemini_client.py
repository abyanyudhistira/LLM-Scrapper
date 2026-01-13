import google.generativeai as genai
from app.utils.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"Initialized Gemini client with model: {GEMINI_MODEL}")
    
    def generate_response(self, prompt: str, max_retries: int = None) -> str:
        """Generate response dari Gemini API dengan retry logic"""
        import time
        
        retries = max_retries or MAX_RETRIES
        
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error calling Gemini API (attempt {attempt + 1}/{retries}): {e}")
                
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Giving up.")
                    raise
