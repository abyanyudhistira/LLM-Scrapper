from app.schemas.profile_schema import LinkedInProfile, Experience, Education
from app.normalizer.experience import calculate_total_experience

def normalize_profile(raw_data: dict) -> LinkedInProfile:
    """Normalisasi data profil mentah ke format standar"""
    experiences = [
        Experience(**exp) for exp in raw_data.get("experiences", [])
    ]
    
    education = [
        Education(**edu) for edu in raw_data.get("education", [])
    ]
    
    total_exp = calculate_total_experience(experiences)
    
    return LinkedInProfile(
        name=raw_data.get("name", ""),
        headline=raw_data.get("headline"),
        experiences=experiences,
        skills=raw_data.get("skills", []),
        education=education,
        total_experience_months=total_exp
    )
