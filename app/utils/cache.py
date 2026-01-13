"""Simple cache untuk hasil matching"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_EXPIRY_HOURS = 24

def get_cache_key(profile_data: dict, requirement_data: dict) -> str:
    """Generate unique cache key dari profile + requirement"""
    combined = json.dumps({
        "profile": profile_data,
        "requirement": requirement_data
    }, sort_keys=True)
    return hashlib.md5(combined.encode()).hexdigest()

def get_cached_result(cache_key: str) -> dict | None:
    """Get cached result jika masih valid"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        
        # Check expiry
        cached_time = datetime.fromisoformat(cached['timestamp'])
        if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
            cache_file.unlink()  # Delete expired cache
            return None
        
        return cached['result']
    except Exception:
        return None

def save_to_cache(cache_key: str, result: dict):
    """Save result to cache"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    cached_data = {
        "timestamp": datetime.now().isoformat(),
        "result": result
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cached_data, f, indent=2, ensure_ascii=False)

def clear_cache():
    """Clear all cache files"""
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
