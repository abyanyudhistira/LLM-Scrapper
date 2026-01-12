import json
from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.schemas.result_schema import MatchResult, RequirementDetail
from app.llm.gemini_client import GeminiClient
from app.llm.prompt import create_matching_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

def evaluate_match(profile: LinkedInProfile, requirement: JobRequirement) -> MatchResult:
    """Evaluasi kecocokan profil dengan requirements menggunakan LLM"""
    
    client = GeminiClient()
    prompt = create_matching_prompt(profile, requirement)
    
    logger.info(f"Evaluating match for {profile.name} - {requirement.job_title}")
    
    response = client.generate_response(prompt)
    
    # Parse JSON response dari LLM
    try:
        # Ekstrak JSON dari response (kadang LLM menambahkan teks di luar JSON)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        json_str = response[json_start:json_end]
        
        result_data = json.loads(json_str)
        
        matched_reqs = [
            RequirementDetail(**req) for req in result_data.get("matched_requirements", [])
        ]
        
        return MatchResult(
            score=result_data.get("score", 0),
            matched_requirements=matched_reqs,
            summary=result_data.get("summary", ""),
            should_send_message=False  # Will be set by score module
        )
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        logger.error(f"Response: {response}")
        raise
