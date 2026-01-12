from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement

def create_matching_prompt(profile: LinkedInProfile, requirement: JobRequirement) -> str:
    """Buat prompt untuk matching profil dengan requirements"""
    
    prompt = f"""Kamu adalah sistem penilaian kecocokan kandidat untuk lowongan pekerjaan.

PROFIL KANDIDAT:
Nama: {profile.name}
Headline: {profile.headline or "Tidak ada"}
Total Pengalaman: {profile.total_experience_months // 12} tahun {profile.total_experience_months % 12} bulan

Pengalaman Kerja:
"""
    
    for exp in profile.experiences:
        prompt += f"- {exp.title} di {exp.company} ({exp.duration_months} bulan)\n"
        if exp.description:
            prompt += f"  Deskripsi: {exp.description}\n"
    
    prompt += f"\nSkills: {', '.join(profile.skills)}\n\n"
    
    prompt += "Pendidikan:\n"
    for edu in profile.education:
        prompt += f"- {edu.degree} dari {edu.institution}"
        if edu.field_of_study:
            prompt += f" ({edu.field_of_study})"
        prompt += "\n"
    
    prompt += f"""
REQUIREMENTS LOWONGAN:
Posisi: {requirement.job_title}
Perusahaan: {requirement.company_name}
Minimal Pengalaman: {requirement.min_experience_years} tahun
Skills yang Dibutuhkan: {', '.join(requirement.required_skills)}
Pendidikan yang Diinginkan: {', '.join(requirement.preferred_education) if requirement.preferred_education else 'Tidak disebutkan'}
"""
    
    if requirement.job_description:
        prompt += f"Deskripsi Pekerjaan: {requirement.job_description}\n"
    
    prompt += """
TUGAS:
Nilai kecocokan kandidat dengan lowongan ini dalam skala 0-100. Berikan output dalam format JSON berikut:

{
  "score": <angka 0-100>,
  "matched_requirements": [
    {
      "requirement": "<nama requirement>",
      "status": "terpenuhi" atau "tidak_terpenuhi",
      "explanation": "<penjelasan singkat>"
    }
  ],
  "summary": "<ringkasan penilaian keseluruhan>"
}

Pertimbangkan:
1. Kecocokan skills (semantik, tidak harus exact match)
2. Pengalaman kerja yang relevan
3. Latar belakang pendidikan
4. Total tahun pengalaman

Berikan penilaian objektif berdasarkan data yang tersedia.
"""
    
    return prompt
