# LinkedIn Profile Matcher

Sistem hybrid matching kandidat dengan job requirements menggunakan Rule-based + Embedding + LLM untuk evaluasi yang akurat dan efisien.

## 🚀 Fitur Utama

### 1. HTML Cleaning & Extraction
- Parse HTML LinkedIn profile dengan BeautifulSoup
- Extract structured data (name, skills, experience, education)
- Convert ke format schema untuk matching

### 2. Hybrid Matching System
- **Rule-based**: Fast filtering berdasarkan experience, skills, education
- **Embedding**: Semantic similarity matching (optional)
- **LLM**: Detailed evaluation dengan Gemini AI (optional)

### 3. Flexible Modes
- **Fast Mode**: Rule-based only (~10ms per candidate)
- **Balanced Mode**: Rule + Embedding (~100ms per candidate)
- **Full Mode**: Rule + Embedding + LLM (~2-3s per candidate)

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dan isi GEMINI_API_KEY
```

## 🎯 Quick Start

### 1. Clean LinkedIn HTML

Simpan HTML LinkedIn profile ke file, lalu jalankan:

```bash
python clean_linkedin_v2.py
```

Output: `data/profiles/linkedin_profile_schema.json`

### 2. Match Profile dengan Requirement

```python
from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.matcher.hybrid import get_hybrid_matcher
import json

# Load profile
with open('data/profiles/linkedin_profile_schema.json', 'r') as f:
    profile_data = json.load(f)
profile = LinkedInProfile(**profile_data)

# Create requirement
requirement = JobRequirement(
    job_title="Senior Backend Engineer",
    company_name="Tech Company",
    required_skills=["Golang", "AWS", "PostgreSQL"],
    min_experience_years=3
)

# Match (Fast Mode)
matcher = get_hybrid_matcher(use_embedding=False, use_llm=False)
result = matcher.match(profile, requirement)

print(f"Score: {result.score}/100")
print(f"Decision: {'SEND MESSAGE' if result.should_send_message else 'SKIP'}")
```

## 📁 Struktur Project

```
├── app/
│   ├── matcher/          # Matching system
│   │   ├── rule_based.py    # Rule-based filtering
│   │   ├── embedding.py     # Semantic matching
│   │   ├── evaluate.py      # LLM evaluation
│   │   └── hybrid.py        # Hybrid matcher
│   ├── schemas/          # Pydantic schemas
│   ├── llm/              # Gemini AI integration
│   └── utils/
│       ├── html_cleaner.py  # HTML cleaning utilities
│       └── cache.py         # Caching
├── data/
│   ├── profiles/         # Candidate profiles
│   └── requirements/     # Job requirements
├── clean_linkedin_v2.py  # LinkedIn HTML cleaner
└── requirements.txt      # Dependencies
```

## 📖 Documentation

- [MATCHING_SYSTEM.md](MATCHING_SYSTEM.md) - Detailed matching system architecture
- [HOW_TO_USE_HTML_CLEANER.md](HOW_TO_USE_HTML_CLEANER.md) - HTML cleaner guide

## 🔧 Configuration

Edit `app/utils/config.py`:

```python
# Matching thresholds
MATCH_THRESHOLD = 70          # Minimum score untuk send message
RULE_BASED_THRESHOLD = 30     # Minimum untuk lanjut ke LLM

# Scoring weights (Full mode)
RULE_WEIGHT = 0.3
EMBEDDING_WEIGHT = 0.2
LLM_WEIGHT = 0.5
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific module
pytest tests/test_normalizer.py
```

## 📊 Performance

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| Fast (Rule only) | ⚡⚡⚡ ~10ms | ⭐⭐ Basic | Batch screening |
| Balanced (Rule + Embedding) | ⚡⚡ ~100ms | ⭐⭐⭐ Good | Balanced |
| Full (+ LLM) | ⚡ ~2-3s | ⭐⭐⭐⭐ Best | Final decision |

## 🎯 Workflow

```
HTML LinkedIn Profile
    ↓
[BeautifulSoup Cleaning] → Structured Data
    ↓
[Rule-based Filter] → Quick filtering (30-40% weight)
    ↓
[Embedding Matching] → Semantic similarity (20% weight)
    ↓
[LLM Evaluation] → Detailed reasoning (50% weight)
    ↓
Final Score & Decision
```

## 📝 License

MIT License
