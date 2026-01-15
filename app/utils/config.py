import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Matching Configuration
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", "70"))  # Threshold untuk send message
AUTO_SEND_THRESHOLD = int(os.getenv("AUTO_SEND_THRESHOLD", "80"))  # Threshold untuk auto-send
RULE_BASED_THRESHOLD = int(os.getenv("RULE_BASED_THRESHOLD", "50"))  # Threshold rule-based minimum
EMBEDDING_SIMILARITY_THRESHOLD = float(os.getenv("EMBEDDING_SIMILARITY_THRESHOLD", "0.5"))  # Threshold embedding similarity

if not 0 <= MATCH_THRESHOLD <= 100:
    raise ValueError("MATCH_THRESHOLD must be between 0 and 100")
if not 0 <= AUTO_SEND_THRESHOLD <= 100:
    raise ValueError("AUTO_SEND_THRESHOLD must be between 0 and 100")
if not 0 <= RULE_BASED_THRESHOLD <= 100:
    raise ValueError("RULE_BASED_THRESHOLD must be between 0 and 100")
if not 0 <= EMBEDDING_SIMILARITY_THRESHOLD <= 1:
    raise ValueError("EMBEDDING_SIMILARITY_THRESHOLD must be between 0 and 1")

# Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # Default to stable model

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Rate Limiting (for batch/queue processing)
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "5"))  # Gemini free tier: 5 RPM for 2.5-flash
BATCH_CHUNK_SIZE = int(os.getenv("BATCH_CHUNK_SIZE", "5"))
DELAY_BETWEEN_CHUNKS = float(os.getenv("DELAY_BETWEEN_CHUNKS", "60.0"))  # 60s between chunks

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    import warnings
    warnings.warn("SUPABASE_URL and SUPABASE_KEY not set. Supabase features will not work.")
    # Set dummy values to prevent crash
    SUPABASE_URL = SUPABASE_URL or "https://dummy.supabase.co"
    SUPABASE_KEY = SUPABASE_KEY or "dummy_key"

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "raw_profiles_queue")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "profiles_exchange")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "raw_profile")
