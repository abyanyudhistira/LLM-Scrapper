"""
Start Worker Script - Run this to start the profile processing worker
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.worker import main

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                   PROFILE PROCESSING WORKER                    ║
    ╚════════════════════════════════════════════════════════════════╝
    
    This worker will:
    1. Listen to RabbitMQ queue for new profiles
    2. Clean and extract profile data from HTML
    3. Match profiles against job requirements
    4. Save results to Supabase
    
    Press CTRL+C to stop the worker
    
    """)
    
    main()
