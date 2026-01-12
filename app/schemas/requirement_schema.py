from pydantic import BaseModel
from typing import List, Optional

class JobRequirement(BaseModel):
    job_title: str
    company_name: str
    required_skills: List[str]
    min_experience_years: Optional[int] = 0
    preferred_education: Optional[List[str]] = []
    job_description: Optional[str] = None
