# LinkedIn Profile Matcher

Sistem untuk mencocokkan profil LinkedIn dengan requirements lowongan pekerjaan menggunakan Gemini AI.

## Fitur

- Normalisasi data profil LinkedIn
- Matching semantik menggunakan LLM (Gemini 2.5 Flash)
- Scoring otomatis (0-100)
- Trigger pengiriman pesan berdasarkan threshold
- Detail requirements yang terpenuhi/tidak terpenuhi

## Setup

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
# atau
make install
```

### 2. Setup API Key Gemini

1. Dapatkan API Key dari [Google AI Studio](https://aistudio.google.com/apikey)
2. Copy file `.env.example` menjadi `.env`
3. Isi dengan API key Anda:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MATCH_THRESHOLD=50
MAX_RETRIES=3
```

**Model yang digunakan:** `gemini-2.5-flash` (configurable)

## Cara Penggunaan

### Opsi 1: Test dengan Script Interaktif (Recommended)

```bash
python test_matching.py
```

Pilih mode test:
- **Mode 1**: Test dengan sample data (langsung jalan)
- **Mode 2**: Test dengan file JSON
- **Mode 3**: Input manual via terminal

### Opsi 2: Test dengan File JSON

1. Buat file profil di `data/profiles/your_profile.json`:

```json
{
  "name": "Ahmad Rizki",
  "headline": "Software Engineer",
  "experiences": [
    {
      "title": "Backend Developer",
      "company": "PT Tech",
      "duration_months": 30,
      "description": "Develop REST API with Django"
    }
  ],
  "skills": ["Python", "Django", "PostgreSQL"],
  "education": [
    {
      "degree": "Sarjana Teknik Informatika",
      "institution": "Universitas Indonesia"
    }
  ]
}
```

2. Buat file requirement di `data/requirements/your_job.json`:

```json
{
  "job_title": "Senior Backend Developer",
  "company_name": "PT Maju Bersama",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "min_experience_years": 3,
  "job_description": "Mencari backend developer berpengalaman"
}
```

3. Jalankan test:

```bash
python test_matching.py
```

Pilih opsi 2, lalu masukkan path file JSON.

### Opsi 3: Gunakan di Code Python

```python
from app.main import process_candidate

profile_data = {
    "name": "John Doe",
    "headline": "Senior Software Engineer",
    "experiences": [
        {
            "title": "Senior Developer",
            "company": "Tech Corp",
            "duration_months": 36,
            "description": "Built REST APIs"
        }
    ],
    "skills": ["Python", "Django", "PostgreSQL"],
    "education": [
        {
            "degree": "Bachelor of Computer Science",
            "institution": "University ABC"
        }
    ]
}

requirement_data = {
    "job_title": "Senior Backend Developer",
    "company_name": "PT Teknologi Maju",
    "required_skills": ["Python", "Django"],
    "min_experience_years": 3
}

result = process_candidate(profile_data, requirement_data)

print(f"Score: {result['score']}/100")
print(f"Should send message: {result['should_send_message']}")
print(f"Summary: {result['summary']}")
```

### Opsi 4: Run Example Bawaan

```bash
python -m app.main
```

## Output Format

Sistem akan menghasilkan output seperti ini:

```
=== HASIL MATCHING ===
Kandidat: Ahmad Rizki
Posisi: Senior Backend Developer
Score: 85/100
Kirim Pesan: Ya

Summary: Kandidat memiliki pengalaman yang relevan dengan posisi yang dibutuhkan...

Detail Requirements:
✓ Python: Kandidat memiliki skill Python dengan pengalaman 4 tahun
✓ Django: Terbukti dari pengalaman kerja di PT Teknologi Digital
✓ PostgreSQL: Disebutkan dalam skills dan pengalaman
✗ Min 5 tahun pengalaman: Kandidat hanya memiliki 4 tahun pengalaman
```

## Struktur Data

### Profile Data (Input)
```json
{
  "name": "string (required)",
  "headline": "string (optional)",
  "experiences": [
    {
      "title": "string (required)",
      "company": "string (required)",
      "duration_months": "number (required)",
      "description": "string (optional)"
    }
  ],
  "skills": ["string array (required)"],
  "education": [
    {
      "degree": "string (required)",
      "institution": "string (required)",
      "field_of_study": "string (optional)"
    }
  ]
}
```

### Requirement Data (Input)
```json
{
  "job_title": "string (required)",
  "company_name": "string (required)",
  "required_skills": ["string array (required)"],
  "min_experience_years": "number (optional, default: 0)",
  "preferred_education": ["string array (optional)"],
  "job_description": "string (optional)"
}
```

### Result Data (Output)
```json
{
  "candidate_name": "string",
  "job_title": "string",
  "score": "number (0-100)",
  "should_send_message": "boolean",
  "message_sent": "boolean",
  "matched_requirements": [
    {
      "requirement": "string",
      "status": "terpenuhi | tidak_terpenuhi",
      "explanation": "string"
    }
  ],
  "summary": "string"
}
```

## Alur Kerja Sistem

```
┌─────────────┐
│   Crawler   │ → Ambil data profil LinkedIn (implementasi disesuaikan)
└──────┬──────┘
       ↓
┌─────────────┐
│ Normalizer  │ → Standarisasi format data profil
└──────┬──────┘
       ↓
┌─────────────┐
│ LLM Matcher │ → Gemini 2.5 Flash menilai kecocokan semantik
└──────┬──────┘
       ↓
┌─────────────┐
│   Scoring   │ → Hitung score (0-100) & apply threshold (≥50)
└──────┬──────┘
       ↓
┌─────────────┐
│   Trigger   │ → Kirim pesan jika score ≥ threshold
└─────────────┘
```

## Testing

### Run Unit Tests

```bash
python -m pytest tests/ -v
# atau
make test
```

### Run Interactive Matching Test

```bash
python test_matching.py
# atau
make test-match
```

### Run Batch Processing Test

```bash
python test_batch.py
```

Process multiple kandidat sekaligus dengan parallel processing.

## Performance Optimizations

### 1. Caching

Sistem otomatis cache hasil matching untuk mengurangi API calls:

```python
# Cache otomatis aktif
result = process_candidate(profile, requirement)  # API call

# Request kedua menggunakan cache (no API call)
result = process_candidate(profile, requirement)  # From cache
```

Cache valid selama 24 jam. Untuk disable cache:

```python
result = process_candidate(profile, requirement, use_cache=False)
```

### 2. Batch Processing

Process multiple kandidat secara parallel:

```python
from app.batch_processor import process_candidates_batch

profiles = [profile1, profile2, profile3, ...]
results = process_candidates_batch(profiles, requirement, max_workers=3)

# Get top candidates
from app.batch_processor import get_top_candidates
top_5 = get_top_candidates(results, top_n=5)
```

### 3. Optimized Prompt

Prompt sudah dioptimasi untuk mengurangi token usage (~60% lebih ringkas) tanpa mengurangi akurasi.

## Konfigurasi

### Threshold Matching

Edit di file `.env`:

```env
MATCH_THRESHOLD=50  # Default: 50, Range: 0-100
```

- Score ≥ threshold → Sistem akan trigger pengiriman pesan
- Score < threshold → Tidak ada aksi

### Ganti Model Gemini

Edit di `app/llm/gemini_client.py`:

```python
self.model = genai.GenerativeModel("gemini-2.5-flash")  # Ganti model di sini
```

Model yang tersedia:
- `gemini-2.5-flash` (Recommended, cepat & akurat)
- `gemini-1.5-pro` (Lebih detail, lebih lambat)
- `gemini-1.5-flash` (Cepat, akurasi standar)

## Troubleshooting

### Error: API Key Invalid
- Pastikan API key benar di file `.env`
- Generate key baru di [Google AI Studio](https://aistudio.google.com/apikey)

### Error: Quota Exceeded
- Model tertentu (seperti `gemini-2.5-pro`) tidak tersedia di free tier
- Gunakan `gemini-2.5-flash` atau `gemini-1.5-flash`

### Error: Module Not Found
```bash
python -m pip install -r requirements.txt
```

## Catatan Penting

- ✅ Sistem ini hanya melakukan **penilaian**, bukan keputusan akhir
- ✅ LLM digunakan untuk **matching semantik**, bukan exact match
- ✅ Threshold default: **50** (dapat diubah di `.env`)
- ⚠️ Implementasi **crawler LinkedIn** perlu disesuaikan dengan tools Anda
- ⚠️ Implementasi **pengiriman pesan** perlu disesuaikan dengan tools Anda

## Lisensi

MIT License
