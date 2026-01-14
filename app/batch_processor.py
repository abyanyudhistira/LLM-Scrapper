"""Batch processing untuk matching multiple kandidat"""
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from app.main import process_candidate
from app.utils.logger import get_logger

logger = get_logger(__name__)

def process_candidates_batch(
    profiles: List[dict],
    requirement: dict,
    max_workers: int = 3,
    chunk_size: int = 10,
    delay_between_chunks: float = 2.0
) -> List[dict]:
    """
    Process multiple kandidat secara parallel dengan chunking
    
    Args:
        profiles: List of profile data
        requirement: Job requirement data
        max_workers: Number of parallel workers per chunk (default: 3)
        chunk_size: Number of profiles per chunk (default: 10)
        delay_between_chunks: Delay in seconds between chunks (default: 2.0)
    
    Returns:
        List of matching results
    """
    total_profiles = len(profiles)
    results = []
    
    logger.info(f"Processing {total_profiles} candidates in chunks of {chunk_size}")
    
    # Split profiles into chunks
    chunks = [profiles[i:i + chunk_size] for i in range(0, total_profiles, chunk_size)]
    total_chunks = len(chunks)
    
    for chunk_idx, chunk in enumerate(chunks, 1):
        logger.info(f"Processing chunk {chunk_idx}/{total_chunks} ({len(chunk)} candidates)")
        
        chunk_results = _process_chunk(chunk, requirement, max_workers)
        results.extend(chunk_results)
        
        # Delay between chunks to avoid rate limit
        if chunk_idx < total_chunks:
            logger.info(f"Waiting {delay_between_chunks}s before next chunk...")
            time.sleep(delay_between_chunks)
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    logger.info(f"Batch processing complete. {len(results)}/{total_profiles} results.")
    return results


def _process_chunk(chunk: List[dict], requirement: dict, max_workers: int) -> List[dict]:
    """Process a single chunk of profiles"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks in chunk
        future_to_profile = {
            executor.submit(process_candidate, profile, requirement): profile
            for profile in chunk
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_profile):
            profile = future_to_profile[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(f"✓ Processed: {result['candidate_name']} - Score: {result['score']}")
            except Exception as e:
                logger.error(f"✗ Failed to process {profile.get('name', 'Unknown')}: {e}")
                results.append({
                    "candidate_name": profile.get('name', 'Unknown'),
                    "error": str(e),
                    "score": 0,
                    "should_send_message": False
                })
    
    return results


def get_top_candidates(results: List[dict], top_n: int = 5) -> List[dict]:
    """Get top N candidates by score"""
    return results[:top_n]


def filter_by_threshold(results: List[dict], threshold: int = 50) -> List[dict]:
    """Filter candidates yang memenuhi threshold"""
    return [r for r in results if r.get('score', 0) >= threshold]
