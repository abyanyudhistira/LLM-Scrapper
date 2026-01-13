import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Matching Configuration
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", "50"))
if not 0 <= MATCH_THRESHOLD <= 100:
    raise ValueError("MATCH_THRESHOLD must be between 0 and 100")

# Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
