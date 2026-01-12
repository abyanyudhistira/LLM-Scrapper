from pydantic import BaseModel
from typing import List, Dict

class RequirementDetail(BaseModel):
    requirement: str
    status: str  # "terpenuhi" atau "tidak_terpenuhi"
    explanation: str

class MatchResult(BaseModel):
    score: int  # 0-100
    matched_requirements: List[RequirementDetail]
    summary: str
    should_send_message: bool
