import google.generativeai as genai
from app.utils.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self, model_name: str = None):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model_name or GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini client with model: {self.model_name}")
    
    def generate_content(self, prompt: str, max_retries: int = None) -> str:
        """
        Generate response dari Gemini API dengan retry logic dan fallback
        
        Args:
            prompt: Prompt untuk Gemini
            max_retries: Jumlah retry maksimal (default dari config)
            
        Returns:
            Response text dari Gemini
            
        Raises:
            Exception: Jika semua retry gagal
        """
        retries = max_retries or MAX_RETRIES
        
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error calling Gemini API (attempt {attempt + 1}/{retries}): {error_msg}")
                
                # Check if it's a rate limit error
                if "429" in error_msg or "quota" in error_msg.lower():
                    # Extract retry delay from error message if available
                    if "retry in" in error_msg.lower():
                        try:
                            # Try to extract seconds from error message
                            import re
                            match = re.search(r'retry in (\d+)', error_msg.lower())
                            if match:
                                suggested_wait = int(match.group(1))
                                wait_time = min(suggested_wait, 60)  # Max 60 seconds
                            else:
                                wait_time = 60  # Default 60 seconds for rate limit
                        except:
                            wait_time = 60
                    else:
                        wait_time = 60
                    
                    logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry...")
                    
                    if attempt < retries - 1:
                        time.sleep(wait_time)
                        continue
                
                # Check if model not found
                elif "404" in error_msg or "not found" in error_msg.lower():
                    logger.error(f"Model {self.model_name} not found. Please check GEMINI_MODEL in .env")
                    logger.info("Available models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp")
                    raise ValueError(f"Invalid model: {self.model_name}")
                
                # For other errors, use exponential backoff
                else:
                    if attempt < retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error("Max retries reached. Giving up.")
                        raise
        
        raise Exception("Failed to generate content after all retries")
    
    def generate_response(self, prompt: str, max_retries: int = None) -> str:
        """Alias untuk backward compatibility"""
        return self.generate_content(prompt, max_retries)
