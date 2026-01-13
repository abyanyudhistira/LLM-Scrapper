import logging
import sys
from pathlib import Path

# Create logs directory if not exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)
