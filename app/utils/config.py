import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", "50"))
