"""Validators untuk input data"""

def validate_profile(profile_data: dict) -> tuple[bool, str]:
    """Validasi data profil sebelum processing"""
    
    required_fields = ["name", "experiences", "skills", "education"]
    
    for field in required_fields:
        if field not in profile_data:
            return False, f"Missing required field: {field}"
    
    if not profile_data["name"]:
        return False, "Name cannot be empty"
    
    if not isinstance(profile_data["experiences"], list) or len(profile_data["experiences"]) == 0:
        return False, "Experiences must be a non-empty list"
    
    if not isinstance(profile_data["skills"], list) or len(profile_data["skills"]) == 0:
        return False, "Skills must be a non-empty list"
    
    return True, "Valid"


def validate_requirement(requirement_data: dict) -> tuple[bool, str]:
    """Validasi data requirement sebelum processing"""
    
    required_fields = ["job_title", "company_name", "required_skills"]
    
    for field in required_fields:
        if field not in requirement_data:
            return False, f"Missing required field: {field}"
    
    if not requirement_data["job_title"]:
        return False, "Job title cannot be empty"
    
    if not isinstance(requirement_data["required_skills"], list) or len(requirement_data["required_skills"]) == 0:
        return False, "Required skills must be a non-empty list"
    
    return True, "Valid"
