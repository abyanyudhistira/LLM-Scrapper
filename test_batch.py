"""Test batch processing multiple candidates"""
import json
from pathlib import Path
from app.batch_processor import process_candidates_batch, get_top_candidates, filter_by_threshold

def load_all_profiles():
    """Load all profiles from data/profiles folder"""
    profiles = []
    profile_dir = Path("data/profiles")
    
    for file in profile_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            profiles.append(json.load(f))
    
    return profiles

def load_requirement(filename):
    """Load specific requirement"""
    with open(f"data/requirements/{filename}", 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    print("="*60)
    print("  BATCH PROCESSING TEST")
    print("="*60)
    
    # Load all profiles
    profiles = load_all_profiles()
    print(f"\nLoaded {len(profiles)} profiles")
    
    # Load requirement
    requirement = load_requirement("senior_backend_strict.json")
    print(f"Requirement: {requirement['job_title']}")
    
    # Process batch
    print("\nProcessing candidates...")
    results = process_candidates_batch(profiles, requirement, max_workers=3)
    
    # Show results
    print("\n" + "="*60)
    print("RESULTS (Sorted by Score)")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['should_send_message'] else "✗ FAIL"
        print(f"{i}. {result['candidate_name']:<25} Score: {result['score']:>3}/100  {status}")
    
    # Top candidates
    print("\n" + "="*60)
    print("TOP 3 CANDIDATES")
    print("="*60)
    
    top_3 = get_top_candidates(results, top_n=3)
    for i, result in enumerate(top_3, 1):
        print(f"\n{i}. {result['candidate_name']} - {result['score']}/100")
        print(f"   Summary: {result['summary'][:100]}...")
    
    # Qualified candidates
    qualified = filter_by_threshold(results, threshold=50)
    print(f"\n{len(qualified)}/{len(results)} candidates qualified (score >= 50)")
