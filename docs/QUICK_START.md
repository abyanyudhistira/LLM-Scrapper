# Quick Start Guide - Queue-Based Processing

Panduan cepat untuk mulai menggunakan sistem queue-based profile processing dengan **existing database**.

## 🚀 5 Menit Setup

### 1. Start RabbitMQ

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

### 2. Setup Database (Existing Supabase)

Kamu sudah punya database dengan tables:
- `scraped_leads` ✅ (sudah punya `score` dan `profile_data`)
- `search_templates` ✅ (sudah punya `job_title` dan `note`)
- `companies` ✅

**✅ NO DATABASE MODIFICATIONS NEEDED!**

Database kamu sudah perfect untuk sistem ini. Tidak perlu add columns atau modify apapun.

### 3. Configure

```bash
cp .env.example .env
nano .env
```

Edit:
```env
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key
```

### 4. Install & Test

```bash
pip install -r requirements.txt
make queue-test
```

Expected output:
```
✓ Connected to RabbitMQ
✓ Queue size: 0 messages
✓ Connected to Supabase
✓ Companies: 3
```

### 5. Start Worker

**Option A: Local (Development)**
```bash
make worker
```

**Option B: Docker (Recommended)**
```bash
make docker-up
```

Output:
```
PROFILE WORKER STARTED
Waiting for messages...
```

**Done!** Worker sekarang running dan siap process profiles.

---

## 📤 Publish Profile (Scraper)

### Message Format

```python
{
    'lead_id': 'uuid-from-scraped-leads',
    'template_id': 'uuid-from-search-templates',
    'html_content': '<html>raw html</html>',
    'matching_mode': 'balanced'  # fast, balanced, or full
}
```

### Simple Example

```python
from app.utils.rabbitmq_client import get_rabbitmq_client

# Connect
rabbitmq = get_rabbitmq_client()

# Publish
rabbitmq.publish({
    'lead_id': 'lead-uuid-from-scraped-leads',
    'template_id': 'template-uuid-from-search-templates',
    'html_content': '<html>raw linkedin html</html>',
    'matching_mode': 'balanced'
})

print("✓ Published!")
```

### Complete Scraper Integration

```python
import uuid
from app.utils.rabbitmq_client import get_rabbitmq_client
from app.utils.supabase_client import get_supabase_client

# 1. Scrape profile
profile_html = scrape_linkedin('https://linkedin.com/in/johndoe')

# 2. Insert to scraped_leads
supabase = get_supabase_client()
lead_data = {
    'id': str(uuid.uuid4()),
    'template_id': 'your-template-id',
    'name': 'John Doe',
    'profile_url': 'https://linkedin.com/in/johndoe',
    'search_url': 'https://linkedin.com/search/...',
    'scraped_at': 'now()'
}

result = supabase.client.table('scraped_leads').insert(lead_data).execute()
lead_id = result.data[0]['id']

# 3. Publish to RabbitMQ
rabbitmq = get_rabbitmq_client()
rabbitmq.publish({
    'lead_id': lead_id,
    'template_id': 'your-template-id',
    'html_content': profile_html,
    'matching_mode': 'balanced'
})

print(f"✓ Published lead {lead_id}")
```

### Batch Processing

```python
# Process multiple profiles
for profile_url in profile_urls:
    # Scrape
    html = scrape_linkedin(profile_url)
    
    # Insert to DB
    lead_id = insert_to_scraped_leads(html, template_id)
    
    # Publish to queue
    rabbitmq.publish({
        'lead_id': lead_id,
        'template_id': template_id,
        'html_content': html,
        'matching_mode': 'fast'  # Use fast mode for batch
    })
```

### Using Publisher Example

```bash
# Copy example to scraper project
cp scripts/publisher_example.py /path/to/scraper/

# Edit and run
python publisher_example.py
```

---

## 🎯 Common Commands

### Local Development
```bash
# Test connection
make queue-test

# Start worker (local)
make worker
```

### Docker Commands (Recommended)
```bash
# Build and start containers
make docker-up

# View logs
make docker-logs

# Restart containers
make docker-restart

# Stop containers
make docker-down

# Check status
make docker-ps

# Scale workers (run 5 workers)
make docker-scale N=5
```

### Alternative Docker Commands
```bash
# Build only
docker-compose build

# Start (with build)
docker-compose up -d --build

# Start without build
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=5

# View logs
docker-compose logs -f worker

# Stop
docker-compose down
```

---

## 🔍 Monitoring

### RabbitMQ UI
- URL: http://localhost:15672
- Login: guest / guest
- Check queue size, message rate

### Supabase Dashboard
- Check `scraped_leads` table for status
- Check `score` for results

### Query Top Candidates

```sql
SELECT * FROM scraped_leads 
WHERE template_id = 'your-template-id' 
  AND score IS NOT NULL
ORDER BY score DESC
LIMIT 10;
```

---

## 🐛 Troubleshooting

### Worker not starting?

```bash
# Check RabbitMQ
docker ps | grep rabbitmq

# Check .env file
cat .env | grep SUPABASE

# Test connection
make queue-test
```

### Messages not processing?

```bash
# Check worker logs
docker-compose logs -f worker

# Check queue size
make queue-test

# Restart worker
docker-compose restart worker
```

### Connection refused?

```bash
# Restart RabbitMQ
docker restart rabbitmq

# Check port
netstat -an | grep 5672
```

---

## 📚 Full Documentation

- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema & queries
- **[README.md](../README.md)** - Main documentation

---

## ✅ Checklist

Setup complete when:

- [ ] RabbitMQ running: `docker ps | grep rabbitmq`
- [ ] `.env` configured with all keys
- [ ] `make queue-test` passes
- [ ] Worker running: `make docker-up` or `make worker`
- [ ] Can publish test message
- [ ] Message processed successfully

---

## 🎉 Next Steps

1. **For You**: Keep worker running 24/7 with Docker
2. **For Scraper Team**: Share this guide
3. **For Production**: Use `docker-compose up -d --scale worker=5`

**System is now fully automated!** 🚀
