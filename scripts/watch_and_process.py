"""
File Watcher - Auto-trigger pipeline saat ada file baru dari scraper
"""

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pipeline import process_pipeline

RAW_HTML_DIR = 'data/raw_html'
CHECK_INTERVAL = 5  # seconds

class HTMLFileHandler(FileSystemEventHandler):
    """Handler untuk detect file HTML baru"""
    
    def __init__(self):
        self.processing = False
    
    def on_created(self, event):
        """Triggered saat file baru dibuat"""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.html'):
            print(f"\n✓ New file detected: {os.path.basename(event.src_path)}")
            
            # Wait a bit untuk ensure file fully written
            time.sleep(2)
            
            # Trigger pipeline
            if not self.processing:
                self.processing = True
                print("\n🚀 Triggering pipeline...")
                try:
                    process_pipeline()
                except Exception as e:
                    print(f"✗ Pipeline error: {e}")
                finally:
                    self.processing = False

def watch_directory():
    """Watch directory untuk file baru"""
    
    print("=" * 80)
    print("FILE WATCHER - AUTO PIPELINE")
    print("=" * 80)
    print()
    print(f"Watching directory: {RAW_HTML_DIR}")
    print("Waiting for new HTML files from scraper...")
    print("Press Ctrl+C to stop")
    print()
    
    # Create directory if not exists
    os.makedirs(RAW_HTML_DIR, exist_ok=True)
    
    # Setup watcher
    event_handler = HTMLFileHandler()
    observer = Observer()
    observer.schedule(event_handler, RAW_HTML_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("✓ Watcher stopped")

if __name__ == "__main__":
    watch_directory()
