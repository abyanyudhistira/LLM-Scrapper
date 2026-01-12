from typing import List
from app.schemas.profile_schema import Experience

def calculate_total_experience(experiences: List[Experience]) -> int:
    """Hitung total pengalaman kerja dalam bulan"""
    return sum(exp.duration_months for exp in experiences)
