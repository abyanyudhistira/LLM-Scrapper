"""Unit tests untuk validators"""
import pytest
from app.utils.validators import validate_profile, validate_requirement

def test_validate_profile_valid():
    profile = {
        "name": "John Doe",
        "experiences": [{"title": "Dev", "company": "A", "duration_months": 12}],
        "skills": ["Python"],
        "education": [{"degree": "BS", "institution": "Uni"}]
    }
    
    is_valid, message = validate_profile(profile)
    assert is_valid == True


def test_validate_profile_missing_name():
    profile = {
        "experiences": [],
        "skills": [],
        "education": []
    }
    
    is_valid, message = validate_profile(profile)
    assert is_valid == False
    assert "name" in message.lower()


def test_validate_requirement_valid():
    requirement = {
        "job_title": "Developer",
        "company_name": "Tech Corp",
        "required_skills": ["Python"]
    }
    
    is_valid, message = validate_requirement(requirement)
    assert is_valid == True


def test_validate_requirement_empty_skills():
    requirement = {
        "job_title": "Developer",
        "company_name": "Tech Corp",
        "required_skills": []
    }
    
    is_valid, message = validate_requirement(requirement)
    assert is_valid == False
