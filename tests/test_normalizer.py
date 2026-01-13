"""Unit tests untuk normalizer"""
import pytest
from app.normalizer.experience import calculate_total_experience
from app.schemas.profile_schema import Experience

def test_calculate_total_experience():
    experiences = [
        Experience(title="Dev", company="A", duration_months=12),
        Experience(title="Senior Dev", company="B", duration_months=24)
    ]
    
    total = calculate_total_experience(experiences)
    assert total == 36


def test_calculate_total_experience_empty():
    experiences = []
    total = calculate_total_experience(experiences)
    assert total == 0
