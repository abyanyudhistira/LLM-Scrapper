# Database Schema - Actual Schema

Dokumentasi untuk database schema yang **benar-benar ada**.

## Actual Tables

### 1. `scraped_leads`

Table untuk menyimpan profile yang sudah di-scrape.

**Existing Fields**:
```sql
- id (uuid) - Primary key
- template_id (uuid) - Foreign key ke search_templates
- name (text) - Nama kandidat
- profile_url (text) - URL LinkedIn profile
- search_url (text) - URL search
- scraped_at (timestamptz) - Waktu scraping
- score (int4) - Score hasil matching (0-100) ✅ SUDAH ADA
- profile_data (jsonb) - Data profile & hasil matching ✅ SUDAH ADA
```

**Tidak perlu add columns!** Table sudah punya `score` dan `profile_data` yang kita butuhkan.

### 2. `search_templates`

Table untuk menyimpan search template (job requirements).

**Existing Fields**:
```sql
- id (uuid) - Primary key
- company_id (uuid) - Foreign key ke companies
- name (text) - Nama template
- job_title (text) - Job title ✅ BISA DIGUNAKAN
- url (text) - Search URL
- note (text) - Notes/description ✅ BISA DIGUNAKAN UNTUK JOB DESCRIPTION
- created_at (timestamptz)
```

### 3. `companies`

Table untuk menyimpan company info.

**Existing Fields**:
```sql
- id (uuid) - Primary key
- name (text) - Nama company
- code (text) - Company code
- created_at (timestamptz)
```

### 4. `connection_history`

Table untuk tracking connection history.

**Existing Fields**:
```sql
- id (uuid) - Primary key
- template_id (uuid) - Foreign key ke search_templates
- date (date) - Tanggal
- leads (jsonb) - Lead data
- created_at (timestamptz)
```

---

## ✅ NO DATABASE MODIFICATIONS NEEDED!

Database kamu **sudah perfect** untuk sistem ini:
- ✅ `scraped_leads.score` - untuk menyimpan match score
- ✅ `scraped_leads.profile_data` - untuk menyimpan extracted profile & match results
- ✅ `search_templates.job_title` - untuk job title
- ✅ `search_templates.note` - untuk job description

---

## How It Works

### 1. Scraper Flow

```sql
-- Scraper insert lead ke scraped_leads
INSERT INTO scraped_leads (
    id,
    template_id,
    name,
    profile_url,
    search_url,
    scraped_at
) VALUES (
    'lead-uuid',
    'template-uuid',
    'John Doe',
    'https://linkedin.com/in/johndoe',
    'https://linkedin.com/search/...',
    NOW()
);
```

### 2. Scraper → RabbitMQ

```python
rabbitmq.publish({
    'lead_id': 'lead-uuid',
    'template_id': 'template-uuid',
    'html_content': '<html>...</html>',
    'matching_mode': 'balanced'
})
```

### 3. Worker → Process → Update

Worker update `scraped_leads`:

```sql
UPDATE scraped_leads 
SET 
    score = 85,
    profile_data = '{
        "extracted_profile": {...},
        "match_result": {
            "score": 85,
            "summary": "Strong match...",
            "breakdown": {...}
        }
    }'::jsonb
WHERE id = 'lead-uuid';
```

---

## Queries

### Get Unscored Leads

```sql
SELECT * FROM scraped_leads 
WHERE score IS NULL
ORDER BY scraped_at ASC
LIMIT 100;
```

### Get Top Candidates by Template

```sql
SELECT 
    sl.*,
    st.job_title,
    c.name as company_name
FROM scraped_leads sl
JOIN search_templates st ON sl.template_id = st.id
JOIN companies c ON st.company_id = c.id
WHERE sl.template_id = 'your-template-id'
  AND sl.score IS NOT NULL
ORDER BY sl.score DESC
LIMIT 10;
```

### Get Template Stats

```sql
SELECT 
    st.id,
    st.job_title,
    c.name as company_name,
    COUNT(sl.id) as total_leads,
    COUNT(sl.score) as scored_leads,
    AVG(sl.score) as avg_score,
    MAX(sl.score) as max_score
FROM search_templates st
JOIN companies c ON st.company_id = c.id
LEFT JOIN scraped_leads sl ON st.id = sl.template_id
GROUP BY st.id, st.job_title, c.name;
```

### Get Profile Data

```sql
SELECT 
    id,
    name,
    score,
    profile_data->'match_result'->>'summary' as match_summary,
    profile_data->'extracted_profile'->>'headline' as headline
FROM scraped_leads
WHERE score >= 70
ORDER BY score DESC;
```

---

## Views (Optional)

### Top Candidates View

```sql
CREATE OR REPLACE VIEW top_candidates AS
SELECT 
    sl.id,
    sl.name,
    sl.profile_url,
    sl.score,
    sl.profile_data->'match_result'->>'summary' as match_summary,
    st.job_title,
    c.name as company_name,
    sl.scraped_at,
    ROW_NUMBER() OVER (PARTITION BY sl.template_id ORDER BY sl.score DESC) as rank
FROM scraped_leads sl
JOIN search_templates st ON sl.template_id = st.id
JOIN companies c ON st.company_id = c.id
WHERE sl.score IS NOT NULL
ORDER BY sl.template_id, sl.score DESC;
```

### Template Stats View

```sql
CREATE OR REPLACE VIEW template_stats AS
SELECT 
    st.id as template_id,
    st.name as template_name,
    st.job_title,
    c.name as company_name,
    COUNT(sl.id) as total_leads,
    COUNT(sl.score) as scored_leads,
    COUNT(CASE WHEN sl.score >= 70 THEN 1 END) as qualified_leads,
    AVG(sl.score) as avg_score,
    MAX(sl.score) as max_score
FROM search_templates st
JOIN companies c ON st.company_id = c.id
LEFT JOIN scraped_leads sl ON st.id = sl.template_id
GROUP BY st.id, st.name, st.job_title, c.name;
```

---

## Integration Example

### Complete Flow

```python
# 1. Scraper scrapes profile
profile_html = scrape_linkedin('https://linkedin.com/in/johndoe')

# 2. Scraper inserts to scraped_leads
lead_id = supabase.table('scraped_leads').insert({
    'template_id': 'template-uuid',
    'name': 'John Doe',
    'profile_url': 'https://linkedin.com/in/johndoe',
    'search_url': 'https://linkedin.com/search/...',
    'scraped_at': datetime.now().isoformat()
}).execute().data[0]['id']

# 3. Scraper publishes to RabbitMQ
rabbitmq.publish({
    'lead_id': lead_id,
    'template_id': 'template-uuid',
    'html_content': profile_html,
    'matching_mode': 'balanced'
})

# 4. Worker processes automatically
# - Extracts profile data
# - Matches with job requirements
# - Updates score and profile_data

# 5. Query results
top_candidates = supabase.table('scraped_leads')\
    .select('*')\
    .eq('template_id', 'template-uuid')\
    .not_.is_('score', 'null')\
    .order('score', desc=True)\
    .limit(10)\
    .execute()
```

---

## Summary

**Perfect Database!** ✅
- No modifications needed
- All required fields already exist
- Ready to use immediately

**Tables Used**:
- ✅ `scraped_leads` - Store profiles & scores
- ✅ `search_templates` - Job requirements
- ✅ `companies` - Company info
- ✅ `connection_history` - History tracking

**Next Steps**:
1. Start RabbitMQ
2. Configure .env
3. Start worker
4. Scraper publish messages

That's it! 🎉
