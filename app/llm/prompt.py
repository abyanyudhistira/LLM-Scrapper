from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement

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
