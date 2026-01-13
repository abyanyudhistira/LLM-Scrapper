from app.normalizer.profile import normalize_profile
from app.requirements.loader import load_requirement_from_dict
from app.matcher.evaluate import evaluate_match
from app.matcher.score import apply_threshold
from app.trigger.send_message import send_linkedin_message
from app.utils.logger import get_logger
from app.utils.validators import validate_profile, validate_requirement
from app.utils.cache import get_cache_key, get_cached_result, save_to_cache

logger = get_logger(__name__)

def process_candidate(profile_data: dict, requirement_data: dict, use_cache: bool = True) -> dict:
    """
    Proses utama: matching kandidat dengan lowongan
    
    Args:
        profile_data: Data profil LinkedIn (dict)
        requirement_data: Data requirements lowongan (dict)
        use_cache: Use cached result if available (default: True)
    
    Returns:
        dict: Hasil matching dengan informasi lengkap
    """
    
    # Check cache first
    if use_cache:
        cache_key = get_cache_key(profile_data, requirement_data)
        cached_result = get_cached_result(cache_key)
        if cached_result:
            logger.info(f"Using cached result for {profile_data.get('name', 'Unknown')}")
            return cached_result
    
    # Validate input data
    is_valid, message = validate_profile(profile_data)
    if not is_valid:
        logger.error(f"Invalid profile data: {message}")
        raise ValueError(f"Invalid profile data: {message}")
    
    is_valid, message = validate_requirement(requirement_data)
    if not is_valid:
        logger.error(f"Invalid requirement data: {message}")
        raise ValueError(f"Invalid requirement data: {message}")
    
    # 1. Normalisasi profil
    profile = normalize_profile(profile_data)
    logger.info(f"Processing candidate: {profile.name}")
    
    # 2. Load requirements
    requirement = load_requirement_from_dict(requirement_data)
    logger.info(f"Job position: {requirement.job_title} at {requirement.company_name}")
    
    # 3. Evaluasi matching dengan LLM
    result = evaluate_match(profile, requirement)
    
    # 4. Apply threshold untuk keputusan pengiriman pesan
    result = apply_threshold(result)
    
    logger.info(f"Match score: {result.score}/100")
    logger.info(f"Should send message: {result.should_send_message}")
    
    # 5. Kirim pesan jika memenuhi threshold
    message_sent = False
    if result.should_send_message:
        message = f"""Halo {profile.name},

Kami tertarik dengan profil Anda untuk posisi {requirement.job_title} di {requirement.company_name}.

Berdasarkan evaluasi, profil Anda memiliki kecocokan {result.score}% dengan requirements kami.

{result.summary}

Apakah Anda tertarik untuk mendiskusikan lebih lanjut?
"""
        message_sent = send_linkedin_message(profile.name, message)
    
    return {
        "candidate_name": profile.name,
        "job_title": requirement.job_title,
        "score": result.score,
        "should_send_message": result.should_send_message,
        "message_sent": message_sent,
        "matched_requirements": [req.model_dump() for req in result.matched_requirements],
        "summary": result.summary
    }
    
    # Save to cache
    if use_cache:
        save_to_cache(cache_key, output)
    
    return output

if __name__ == "__main__":
    # Contoh penggunaan
    sample_profile = {
        "name": "John Doe",
        "headline": "Senior Software Engineer",
        "experiences": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration_months": 36,
                "description": "Developed web applications using Python and React"
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "duration_months": 24,
                "description": "Built REST APIs and microservices"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "Django", "PostgreSQL", "Docker"],
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "institution": "University ABC",
                "field_of_study": "Computer Science"
            }
        ]
    }
    
    sample_requirement = {
        "job_title": "Senior Backend Developer",
        "company_name": "PT Teknologi Maju",
        "required_skills": ["Python", "Django", "PostgreSQL", "REST API"],
        "min_experience_years": 3,
        "preferred_education": ["Bachelor of Computer Science", "Bachelor of Information Technology"],
        "job_description": "Mencari backend developer berpengalaman untuk membangun sistem enterprise"
    }
    
    result = process_candidate(sample_profile, sample_requirement)
    
    print("\n=== HASIL MATCHING ===")
    print(f"Kandidat: {result['candidate_name']}")
    print(f"Posisi: {result['job_title']}")
    print(f"Score: {result['score']}/100")
    print(f"Kirim Pesan: {result['should_send_message']}")
    print(f"\nSummary: {result['summary']}")
