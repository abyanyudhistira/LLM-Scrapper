# LinkedIn Profile Matcher

Sistem untuk mencocokkan profil LinkedIn dengan requirements lowongan pekerjaan menggunakan Gemini API.

## Fitur

- Normalisasi data profil LinkedIn
- Matching semantik menggunakan LLM (Gemini)
- Scoring otomatis (0-100)
- Trigger pengiriman pesan berdasarkan threshold
- Detail requirements yang terpenuhi/tidak terpenuhi

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup API Key di file `.env`:
```
GEMINI_API_KEY=your_api_key_here
MATCH_THRESHOLD=50
```

3. Dapatkan API Key dari [Google AI Studio](https://makersuite.google.com/app/apikey)

## Cara Penggunaan

### Basic Usage

```python
from app.main import process_candidate

profile_data = {
    "name": "John Doe",
    "headline": "Senior Software Engineer",
    "experiences": [...],
    "skills": [...],
    "education": [...]
}

requirement_data = {
    "job_title": "Senior Backend Developer",
    "company_name": "PT Teknologi Maju",
    "required_skills": ["Python", "Django"],
    "min_experience_years": 3
}

result = process_candidate(profile_data, requirement_data)
print(f"Score: {result['score']}/100")
```

### Run Example

```bash
python app/main.py
```

## Struktur Data

### Profile Data
```json
{
  "name": "string",
  "headline": "string",
  "experiences": [
    {
      "title": "string",
      "company": "string",
      "duration_months": 36,
      "description": "string"
    }
  ],
  "skills": ["skill1", "skill2"],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "field_of_study": "string"
    }
  ]
}
```

### Requirement Data
```json
{
  "job_title": "string",
  "company_name": "string",
  "required_skills": ["skill1", "skill2"],
  "min_experience_years": 3,
  "preferred_education": ["degree1"],
  "job_description": "string"
}
```

## Alur Kerja

1. **Crawler** → Ambil data profil LinkedIn (implementasi disesuaikan)
2. **Normalizer** → Standarisasi format data
3. **LLM Matching** → Gemini API menilai kecocokan
4. **Scoring** → Hitung score dan apply threshold
5. **Trigger** → Kirim pesan jika score ≥ threshold

## Catatan

- Sistem ini hanya melakukan penilaian, bukan keputusan akhir
- LLM digunakan untuk matching semantik, bukan exact match
- Threshold default: 50 (dapat diubah di .env)
- Implementasi crawler dan pengiriman pesan perlu disesuaikan dengan tools Anda
