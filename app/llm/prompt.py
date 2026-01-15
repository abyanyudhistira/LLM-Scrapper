from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement

def create_extraction_prompt(cleaned_text: str) -> str:
    """Buat prompt untuk extract profile data dari cleaned HTML text"""
    
    prompt = f"""Extract LinkedIn profile information from the following text and return as JSON.

TEXT:
{cleaned_text[:3000]}  # Limit to 3000 chars

Extract these fields:
- name: Full name
- headline: Current position/headline
- experiences: Array of {{title, company, duration_months, description}}
- skills: Array of skill names
- education: Array of {{degree, institution, field_of_study}}
- total_experience_months: Total work experience in months

OUTPUT (JSON only, no markdown):
{{
  "name": "Full Name",
  "headline": "Current Position",
  "experiences": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration_months": 24,
      "description": "Brief description"
    }}
  ],
  "skills": ["Skill1", "Skill2", "Skill3"],
  "education": [
    {{
      "degree": "Bachelor's Degree",
      "institution": "University Name",
      "field_of_study": "Computer Science"
    }}
  ],
  "total_experience_months": 60
}}

Rules:
- Calculate total_experience_months from all experiences
- If information not found, use empty array [] or "Unknown"
- Return valid JSON only
"""
    
    return prompt

def create_matching_prompt(profile: LinkedInProfile, requirement: JobRequirement) -> str:
    """Buat prompt untuk matching profil dengan requirements"""
    
    # Ringkas pengalaman
    exp_summary = []
    for exp in profile.experiences:
        years = exp.duration_months / 12
        exp_summary.append(f"- {exp.title} ({years:.1f}y)")
    
    prompt = f"""Nilai kecocokan kandidat untuk lowongan (0-100).

KANDIDAT:
Nama: {profile.name}
Total Exp: {profile.total_experience_months // 12}y {profile.total_experience_months % 12}m
Posisi: {profile.headline or "N/A"}
Riwayat: {', '.join(exp_summary)}
Skills: {', '.join(profile.skills[:10])}  # Limit 10 skills
Pendidikan: {profile.education[0].degree if profile.education else "N/A"}

LOWONGAN:
Posisi: {requirement.job_title}
Min Exp: {requirement.min_experience_years}y
Skills: {', '.join(requirement.required_skills)}

OUTPUT (JSON only):
{{
  "score": <0-100>,
  "matched_requirements": [
    {{"requirement": "<skill/exp>", "status": "terpenuhi/tidak_terpenuhi", "explanation": "<singkat>"}}
  ],
  "summary": "<1-2 kalimat>"
}}

Pertimbangkan: skill match (semantik), pengalaman relevan, total tahun kerja."""
    
    return prompt
