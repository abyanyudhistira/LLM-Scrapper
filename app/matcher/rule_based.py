"""
Rule-based Matching System
Matching berdasarkan aturan eksplisit sebelum LLM
"""

from typing import List, Dict, Tuple
from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.utils.logger import get_logger
from app.utils.config import RULE_BASED_THRESHOLD

logger = get_logger(__name__)


def calculate_experience_match(profile: LinkedInProfile, requirement: JobRequirement) -> Tuple[bool, int]:
    """
    Hitung kecocokan pengalaman kerja
    
    Returns:
        (is_match, score_contribution)
    """
    total_years = profile.total_experience_months / 12
    required_years = requirement.min_experience_years or 0
    
    if total_years >= required_years:
        # Bonus jika lebih dari requirement
        if total_years >= required_years * 1.5:
            return True, 30
        return True, 25
    elif total_years >= required_years * 0.8:
        # Masih acceptable jika 80% dari requirement
        return True, 15
    else:
        return False, 0


def calculate_skills_match(profile: LinkedInProfile, requirement: JobRequirement) -> Tuple[int, int, List[str]]:
    """
    Hitung kecocokan skills
    
    Returns:
        (matched_count, score_contribution, matched_skills)
    """
    profile_skills_lower = [skill.lower() for skill in profile.skills]
    required_skills_lower = [skill.lower() for skill in requirement.required_skills]
    
    matched_skills = []
    for req_skill in required_skills_lower:
        # Exact match atau partial match
        for prof_skill in profile_skills_lower:
            if req_skill in prof_skill or prof_skill in req_skill:
                matched_skills.append(req_skill)
                break
    
    matched_count = len(matched_skills)
    total_required = len(requirement.required_skills)
    
    if total_required == 0:
        return 0, 0, []
    
    match_percentage = matched_count / total_required
    
    # Scoring berdasarkan persentase match
    if match_percentage >= 0.8:
        score = 40
    elif match_percentage >= 0.6:
        score = 30
    elif match_percentage >= 0.4:
        score = 20
    else:
        score = int(match_percentage * 40)
    
    return matched_count, score, matched_skills


def calculate_education_match(profile: LinkedInProfile, requirement: JobRequirement) -> Tuple[bool, int]:
    """
    Hitung kecocokan pendidikan
    
    Returns:
        (is_match, score_contribution)
    """
    if not requirement.preferred_education:
        return True, 10  # No specific requirement
    
    profile_degrees = [edu.degree.lower() for edu in profile.education]
    preferred_degrees = [deg.lower() for deg in requirement.preferred_education]
    
    for pref_deg in preferred_degrees:
        for prof_deg in profile_degrees:
            if pref_deg in prof_deg or prof_deg in pref_deg:
                return True, 20
    
    # Tidak match tapi masih ada pendidikan
    if profile.education:
        return False, 5
    
    return False, 0


def rule_based_scoring(profile: LinkedInProfile, requirement: JobRequirement) -> Dict:
    """
    Scoring berdasarkan aturan eksplisit
    
    Returns:
        Dictionary dengan hasil scoring dan detail
    """
    results = {
        'total_score': 0,
        'experience': {},
        'skills': {},
        'education': {},
        'passed_threshold': False
    }
    
    # Experience matching
    exp_match, exp_score = calculate_experience_match(profile, requirement)
    results['experience'] = {
        'matched': exp_match,
        'score': exp_score,
        'profile_years': profile.total_experience_months / 12,
        'required_years': requirement.min_experience_years or 0
    }
    results['total_score'] += exp_score
    
    # Skills matching
    matched_count, skills_score, matched_skills = calculate_skills_match(profile, requirement)
    results['skills'] = {
        'matched_count': matched_count,
        'total_required': len(requirement.required_skills),
        'score': skills_score,
        'matched_skills': matched_skills
    }
    results['total_score'] += skills_score
    
    # Education matching
    edu_match, edu_score = calculate_education_match(profile, requirement)
    results['education'] = {
        'matched': edu_match,
        'score': edu_score
    }
    results['total_score'] += edu_score
    
    # Threshold check
    results['passed_threshold'] = results['total_score'] >= RULE_BASED_THRESHOLD
    
    logger.info(f"Rule-based score: {results['total_score']}/100 (threshold: {RULE_BASED_THRESHOLD})")
    
    return results


def should_use_llm(rule_based_result: Dict) -> bool:
    """
    Tentukan apakah perlu menggunakan LLM untuk evaluasi lebih detail
    
    Args:
        rule_based_result: Hasil dari rule_based_scoring
        
    Returns:
        True jika perlu LLM, False jika sudah jelas tidak cocok
    """
    score = rule_based_result['total_score']
    
    # Jika score terlalu rendah, tidak perlu LLM
    if score < 30:
        logger.info("Score too low, skipping LLM evaluation")
        return False
    
    # Jika score borderline atau tinggi, gunakan LLM untuk detail
    logger.info("Score sufficient, will use LLM for detailed evaluation")
    return True
