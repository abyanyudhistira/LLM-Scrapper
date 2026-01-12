from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    title: str
    company: str
    duration_months: int
    description: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    field_of_study: Optional[str] = None

class LinkedInProfile(BaseModel):
    name: str
    headline: Optional[str] = None
    experiences: List[Experience]
    skills: List[str]
    education: List[Education]
    total_experience_months: int = 0
