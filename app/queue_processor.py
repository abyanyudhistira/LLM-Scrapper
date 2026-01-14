"""Queue-based processing untuk handle large volume"""
import queue
import threading
import time
from typing import List, Callable
from app.main import process_candidate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MatchingQueue:
    """Queue system untuk processing kandidat dengan rate limiting"""
    
    def __init__(
        self,
        requirement: dict,
        max_workers: int = 3,
        requests_per_minute: int = 15,
        on_complete: Callable = None
    ):
        """
        Initialize queue processor
        
        Args:
            requirement: Job requirement data
            max_workers: Number of concurrent workers
            requests_per_minute: Max API calls per minute (default: 15 for free tier)
            on_complete: Callback function when a profile is processed
        """
        self.requirement = requirement
        self.max_workers = max_workers
        self.requests_per_minute = requests_per_minute
        self.on_complete = on_complete
        
        self.task_queue = queue.Queue()
        self.results = []
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        # Rate limiting
        self.request_times = []
        self.rate_limit_lock = threading.Lock()
    
    def add_profiles(self, profiles: List[dict]):
        """Add profiles to queue"""
        for profile in profiles:
            self.task_queue.put(profile)
            self.total_tasks += 1
        
        logger.info(f"Added {len(profiles)} profiles to queue. Total: {self.total_tasks}")
    
    def _wait_for_rate_limit(self):
        """Wait if rate limit is reached"""
        with self.rate_limit_lock:
            now = time.time()
            
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            # Check if we've hit the limit
            if len(self.request_times) >= self.requests_per_minute:
                oldest_request = self.request_times[0]
                wait_time = 60 - (now - oldest_request)
                
                if wait_time > 0:
                    logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    # Clear old requests after waiting
                    self.request_times = []
            
            # Record this request
            self.request_times.append(time.time())
    
    def _worker(self):
        """Worker thread to process profiles"""
        while True:
            try:
                # Get profile from queue (with timeout)
                profile = self.task_queue.get(timeout=1)
                
                # Wait for rate limit
                self._wait_for_rate_limit()
                
                # Process profile
                try:
                    result = process_candidate(profile, self.requirement)
                    self.results.append(result)
                    self.completed_tasks += 1
                    
                    logger.info(
                        f"✓ [{self.completed_tasks}/{self.total_tasks}] "
                        f"{result['candidate_name']} - Score: {result['score']}"
                    )
                    
                    # Call callback if provided
                    if self.on_complete:
                        self.on_complete(result)
                
                except Exception as e:
                    self.failed_tasks += 1
                    logger.error(f"✗ Failed to process {profile.get('name', 'Unknown')}: {e}")
                    
                    self.results.append({
                        "candidate_name": profile.get('name', 'Unknown'),
                        "error": str(e),
                        "score": 0,
                        "should_send_message": False
                    })
                
                finally:
                    self.task_queue.task_done()
            
            except queue.Empty:
                # No more tasks, exit worker
                break
    
    def process(self) -> List[dict]:
        """Start processing queue"""
        logger.info(f"Starting queue processing with {self.max_workers} workers")
        logger.info(f"Rate limit: {self.requests_per_minute} requests/minute")
        
        start_time = time.time()
        
        # Start worker threads
        threads = []
        for i in range(self.max_workers):
            thread = threading.Thread(target=self._worker, name=f"Worker-{i+1}")
            thread.start()
            threads.append(thread)
        
        # Wait for all tasks to complete
        self.task_queue.join()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        elapsed_time = time.time() - start_time
        
        # Sort results by score
        self.results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Queue processing complete in {elapsed_time:.1f}s")
        logger.info(f"Completed: {self.completed_tasks}, Failed: {self.failed_tasks}")
        
        return self.results
    
    def get_progress(self) -> dict:
        """Get current progress"""
        return {
            "total": self.total_tasks,
            "completed": self.completed_tasks,
            "failed": self.failed_tasks,
            "pending": self.task_queue.qsize(),
            "progress_percent": (self.completed_tasks / self.total_tasks * 100) if self.total_tasks > 0 else 0
        }


def process_with_queue(
    profiles: List[dict],
    requirement: dict,
    max_workers: int = 3,
    requests_per_minute: int = 15
) -> List[dict]:
    """
    Convenience function untuk queue processing
    
    Args:
        profiles: List of profile data
        requirement: Job requirement data
        max_workers: Number of concurrent workers
        requests_per_minute: Max API calls per minute
    
    Returns:
        List of matching results
    """
    queue_processor = MatchingQueue(
        requirement=requirement,
        max_workers=max_workers,
        requests_per_minute=requests_per_minute
    )
    
    queue_processor.add_profiles(profiles)
    return queue_processor.process()
