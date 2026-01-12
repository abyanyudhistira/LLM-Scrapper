import json
from pathlib import Path
from app.schemas.requirement_schema import JobRequirement

def load_requirement_from_json(file_path: str) -> JobRequirement:
    """Load requirements dari file JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JobRequirement(**data)

def load_requirement_from_dict(data: dict) -> JobRequirement:
    """Load requirements dari dictionary"""
    return JobRequirement(**data)
