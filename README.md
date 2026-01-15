# LinkedIn Profile Matcher

Sistem hybrid matching kandidat dengan job requirements menggunakan Rule-based + Embedding + LLM untuk evaluasi yang akurat dan efisien.

**NEW**: Sekarang dengan **RabbitMQ Queue** dan **Supabase Database** integration untuk automated processing!

## 🚀 Fitur Utama

### 1. Automated Queue Processing (NEW!)
- **RabbitMQ Integration**: Queue-based processing untuk handle banyak profile
- **Supabase Database**: Persistent storage untuk profiles dan results
- **Auto Worker**: Worker yang always running, otomatis process profile baru
- **Scalable**: Support multiple workers untuk parallel processing

### 2. HTML Cleaning & Extraction
- Parse HTML LinkedIn profile dengan BeautifulSoup
- Extract structured data (name, skills, experience, education)
- Convert ke format schema untuk matching

### 3. Hybrid Matching System
- **Rule-based**: Fast filtering berdasarkan experience, skills, education
- **Embedding**: Semantic similarity matching (optional)
- **LLM**: Detailed evaluation dengan Gemini AI (optional)

### 4. Flexible Modes
- **Fast Mode**: Rule-based only (~10ms per candidate)
- **Balanced Mode**: Rule + Embedding (~100ms per candidate)
- **Full Mode**: Rule + Embedding + LLM (~2-3s per candidate)

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dan isi:
# - GEMINI_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
# - RABBITMQ_HOST (default: localhost)
```

## 🔄 Queue-Based Processing (NEW!)

### Quick Start

```bash
# 1. Start RabbitMQ (with Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

# 2. Setup Supabase tables
# Run scripts/setup_supabase.sql in Supabase SQL Editor

# 3. Test connection
make queue-test

# 4. Start worker (always running)
make worker
```

### How It Works

```
Scraper → Publish to RabbitMQ → Worker (always listening) → Process → Save to Supabase
```

1. **Scraper** (teman kamu) scraping LinkedIn → publish raw HTML ke RabbitMQ
2. **Worker** (program ini) otomatis consume message dari queue
3. **Processing**: Clean → Extract → Match → Score
4. **Save** hasil ke Supabase database

### For Scraper (Integration)

```python
# Scraper publish profile ke queue
from app.utils.rabbitmq_client import get_rabbitmq_client

rabbitmq = get_rabbitmq_client()
rabbitmq.publish({
    'profile_id': 'unique-id',
    'job_id': 'job-uuid-from-supabase',
    'html_content': raw_html_string,
    'matching_mode': 'balanced'
})
```

Lihat `scripts/publisher_example.py` untuk contoh lengkap.

### Documentation

📖 **[QUEUE_SETUP.md](docs/QUEUE_SETUP.md)** - Complete setup guide untuk RabbitMQ + Supabase

---

## 🎯 Quick Start

### Single Entry Point CLI

Semua operasi dilakukan melalui `run.py`:

```bash
# Run pipeline once (process all HTML files)
python run.py pipeline

# Run pipeline with full LLM evaluation
python run.py pipeline --mode full

# Watch for new HTML files (auto-process)
python run.py watch

# Watch with balanced mode
python run.py watch --mode balanced

# Match single profile
python run.py match data/profiles/candidate.json

# Match with custom requirement
python run.py match data/profiles/candidate.json --requirement data/requirements/job.json
```

### Matching Modes

- **fast**: Rule-based only (~10ms per candidate)
- **balanced**: Rule + Embedding (~100ms per candidate)  
- **full**: Rule + Embedding + LLM (~2-3s per candidate)

### Pipeline Workflow

1. Place LinkedIn HTML files in `data/raw_html/`
2. Run `python run.py pipeline`
3. Results saved to `data/results/`
4. Processed files moved to `data/raw_html/processed/`

## 📁 Struktur Project

```
├── app/
│   ├── matcher/          # Matching system
│   │   ├── rule_based.py    # Rule-based filtering
│   │   ├── embedding.py     # Semantic matching
│   │   ├── evaluate.py      # LLM evaluation
│   │   ├── hybrid.py        # Hybrid matcher
│   │   └── score.py         # Threshold application
│   ├── schemas/          # Pydantic schemas
│   ├── llm/              # Gemini AI integration
│   ├── normalizer/       # Profile normalization
│   └── utils/
│       ├── html_cleaner.py  # HTML cleaning utilities
│       ├── config.py        # Centralized configuration
│       └── cache.py         # Caching
├── scripts/
│   └── pipeline.py       # Automated pipeline
├── data/
│   ├── raw_html/         # Input HTML files
│   ├── profiles/         # Extracted profiles
│   ├── requirements/     # Job requirements
│   └── results/          # Pipeline results
├── run.py                # Main CLI entry point
└── requirements.txt      # Dependencies
```

## 📖 Documentation

### Queue-Based Processing
- **[QUICK_START.md](QUICK_START.md)** - 5 menit setup guide ⚡
- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Database schema & queries

### Matching System
- [MATCHING_SYSTEM.md](MATCHING_SYSTEM.md) - Detailed matching system architecture
- [HOW_TO_USE_HTML_CLEANER.md](HOW_TO_USE_HTML_CLEANER.md) - HTML cleaner guide

## 🔧 Configuration

All thresholds are centralized in `app/utils/config.py` and can be configured via `.env`:

```bash
# Matching thresholds (0-100)
MATCH_THRESHOLD=70              # Minimum score to send message
AUTO_SEND_THRESHOLD=80          # Minimum score for auto-send
RULE_BASED_THRESHOLD=50         # Minimum rule-based score to proceed
EMBEDDING_SIMILARITY_THRESHOLD=0.5  # Embedding similarity threshold (0-1)

# Model configuration
GEMINI_MODEL=gemini-2.5-flash
MAX_RETRIES=3
```

### Scoring Weights (Full Mode)

- Rule-based: 30%
- Embedding: 20%
- LLM: 50%

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

### Traditional Pipeline (File-based)
```
LinkedIn HTML Files (data/raw_html/)
    ↓
[HTML Cleaner] → Clean text with BeautifulSoup
    ↓
[LLM Extraction] → Structured profile data
    ↓
[Rule-based Filter] → Quick filtering (threshold: 50)
    ↓
[Embedding Matching] → Semantic similarity (optional)
    ↓
[LLM Evaluation] → Detailed reasoning (optional)
    ↓
[Threshold Check] → Score >= 70 → Send message
    ↓
[Auto-send] → Score >= 80 → Auto-send without review
    ↓
Results saved to data/results/
```

### Queue-Based Processing (NEW!)
```
Scraper → RabbitMQ Queue → Worker (always running)
                              ↓
                        [Clean & Extract]
                              ↓
                        [Match & Score]
                              ↓
                        Save to Supabase
                              ↓
                        Update status
```

## 📝 License

MIT License
