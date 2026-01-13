"""Batch processing untuk matching multiple kandidat"""
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.main import process_candidate
from app.utils.logger import get_logger

logger = get_logger(__name__)

def process_candidates_batch(
    profiles: List[dict],
    requirement: dict,
    max_workers: int = 3
) -> List[dict]:
    """
    Process multiple kandidat secara parallel
    
    Args:
        profiles: List of profile data
        requirement: Job requirement data
        max_workers: Number of parallel workers (default: 3)
    
    Returns:
        List of matching results
    """
    results = []
    
    logger.info(f"Processing {len(profiles)} candidates with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_profile = {
            executor.submit(process_candidate, profile, requirement): profile
            for profile in profiles
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
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    logger.info(f"Batch processing complete. {len(results)} results.")
    return results


def get_top_candidates(results: List[dict], top_n: int = 5) -> List[dict]:
    """Get top N candidates by score"""
    return results[:top_n]


def filter_by_threshold(results: List[dict], threshold: int = 50) -> List[dict]:
    """Filter candidates yang memenuhi threshold"""
    return [r for r in results if r.get('score', 0) >= threshold]
