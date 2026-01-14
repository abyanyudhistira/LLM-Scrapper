"""
Automated Pipeline: Scraper → Cleaner → Matcher
Trigger otomatis untuk process profile dari scraper
"""

from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.matcher.hybrid import get_hybrid_matcher
from app.utils.html_cleaner import clean_html
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Job Requirement
JOB_TITLE = "Senior Backend Developer"
COMPANY_NAME = "Tech Company ABC"
REQUIRED_SKILLS = ["Python", "Django", "PostgreSQL", "Docker"]
MIN_EXPERIENCE_YEARS = 3
PREFERRED_EDUCATION = ["Sarjana Teknik Informatika"]

# Matching Mode
MATCHING_MODE = 'fast'  # 'fast', 'balanced', 'full'

# Directories
RAW_HTML_DIR = 'data/raw_html'  # Input dari scraper
PROFILES_DIR = 'data/profiles'
RESULTS_DIR = 'data/results'

# Auto-send threshold
AUTO_SEND_THRESHOLD = 50  # Score >= 50 akan auto-send

# ============================================================================

def clean_and_extract(html_content, filename):
    """
    Clean HTML dan extract data menjadi profile JSON
    
    Args:
        html_content: Raw HTML dari scraper
        filename: Nama file untuk tracking
        
    Returns:
        LinkedInProfile object atau None jika gagal
    """
    print(f"  Cleaning {filename}...", end=' ')
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract name
        name = "Unknown"
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            text = h1.get_text(strip=True)
            if 5 < len(text) < 100 and not text.startswith('About'):
                name = text
                break
        
        # Extract headline
        headline = ""
        text_elements = soup.find_all(string=re.compile(r'(Engineer|Developer|Mentor|Backend|Frontend|Golang|Javascript)', re.I))
        for elem in text_elements:
            text = elem.strip()
            if 10 < len(text) < 150 and '|' in text:
                headline = text
                break
        
        # Extract skills
        skills = []
        skill_keywords = ['Go', 'Golang', 'JavaScript', 'Python', 'Java', 'AWS', 'GCP', 
                         'PostgreSQL', 'MongoDB', 'MySQL', 'Docker', 'Kubernetes', 
                         'React', 'Node.js', 'Django', 'Flask', 'Spring Boot']
        text_content = soup.get_text()
        for skill in skill_keywords:
            if skill in text_content:
                skills.append(skill)
        
        # Extract experience (simplified)
        experiences = []
        exp_years = re.findall(r'(\d+)\+?\s*years?', text_content, re.I)
        total_months = int(exp_years[0]) * 12 if exp_years else 24
        
        # Create dummy experience (akan di-improve dengan parser yang lebih baik)
        experiences.append({
            'title': headline.split('|')[0].strip() if '|' in headline else 'Software Engineer',
            'company': 'Company',
            'duration_months': total_months,
            'description': ''
        })
        
        # Extract education (simplified)
        education = []
        edu_keywords = ['University', 'Universitas', 'Institut', 'Politeknik']
        for keyword in edu_keywords:
            if keyword in text_content:
                education.append({
                    'degree': 'Sarjana',
                    'institution': keyword,
                    'field_of_study': 'Computer Science'
                })
                break
        
        if not education:
            education.append({
                'degree': 'N/A',
                'institution': 'N/A',
                'field_of_study': None
            })
        
        # Create profile
        from app.schemas.profile_schema import Experience, Education
        
        profile = LinkedInProfile(
            name=name,
            headline=headline,
            experiences=[Experience(**exp) for exp in experiences],
            skills=list(set(skills)),
            education=[Education(**edu) for edu in education],
            total_experience_months=total_months
        )
        
        print(f"✓ {name}")
        return profile
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def save_profile(profile, filename):
    """Save profile to JSON"""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    
    # Generate filename
    safe_name = profile.name.replace(' ', '_').replace('/', '_')
    output_file = f'{PROFILES_DIR}/{safe_name}.json'
    
    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(profile.model_dump_json(indent=2))
    
    return output_file

def match_profile(profile, requirement, matcher):
    """Match profile dengan requirement"""
    try:
        result = matcher.match(profile, requirement)
        return result
    except Exception as e:
        print(f"    ✗ Matching error: {e}")
        return None

def send_message(profile, score, summary):
    """
    Trigger untuk kirim pesan (placeholder)
    Implement sesuai dengan sistem messaging yang digunakan
    """
    print(f"    📧 Sending message to {profile.name}...")
    
    # TODO: Implement actual message sending
    # Contoh:
    # - LinkedIn API
    # - Email
    # - WhatsApp
    # - Telegram
    # - Webhook ke sistem lain
    
    message = f"""
    Hi {profile.name},
    
    Kami tertarik dengan profile Anda untuk posisi {JOB_TITLE}.
    
    {summary}
    
    Apakah Anda tertarik untuk diskusi lebih lanjut?
    """
    
    # Simulate sending
    print(f"    ✓ Message sent! (Score: {score}/100)")
    
    return True

def process_pipeline():
    """Main pipeline: Scraper → Cleaner → Matcher → Sender"""
    
    print("=" * 80)
    print("AUTOMATED PIPELINE")
    print("=" * 80)
    print()
    
    # 1. Check for new HTML files
    print("1. Checking for new profiles from scraper...")
    
    if not os.path.exists(RAW_HTML_DIR):
        os.makedirs(RAW_HTML_DIR)
        print(f"   ✗ No raw HTML directory found")
        print(f"   Created: {RAW_HTML_DIR}")
        print(f"   Place HTML files from scraper here")
        return
    
    html_files = [f for f in os.listdir(RAW_HTML_DIR) if f.endswith('.html')]
    
    if not html_files:
        print(f"   ✗ No HTML files found in {RAW_HTML_DIR}")
        print(f"   Waiting for scraper to add files...")
        return
    
    print(f"   ✓ Found {len(html_files)} HTML files")
    print()
    
    # 2. Create requirement
    print("2. Job Requirement:")
    requirement = JobRequirement(
        job_title=JOB_TITLE,
        company_name=COMPANY_NAME,
        required_skills=REQUIRED_SKILLS,
        min_experience_years=MIN_EXPERIENCE_YEARS,
        preferred_education=PREFERRED_EDUCATION
    )
    print(f"   Position: {requirement.job_title}")
    print(f"   Skills: {', '.join(requirement.required_skills)}")
    print()
    
    # 3. Initialize matcher
    print(f"3. Initializing matcher (Mode: {MATCHING_MODE})...")
    if MATCHING_MODE == 'fast':
        matcher = get_hybrid_matcher(use_embedding=False, use_llm=False)
    elif MATCHING_MODE == 'balanced':
        matcher = get_hybrid_matcher(use_embedding=True, use_llm=False)
    else:
        matcher = get_hybrid_matcher(use_embedding=True, use_llm=True)
    print("   ✓ Matcher ready")
    print()
    
    # 4. Process each HTML file
    print("4. Processing profiles...")
    print("-" * 80)
    
    results = []
    processed_files = []
    
    for i, html_file in enumerate(html_files, 1):
        print(f"\n[{i}/{len(html_files)}] Processing {html_file}")
        
        # Read HTML
        html_path = os.path.join(RAW_HTML_DIR, html_file)
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean & Extract
        profile = clean_and_extract(html_content, html_file)
        
        if not profile:
            continue
        
        # Save profile JSON
        profile_file = save_profile(profile, html_file)
        print(f"  ✓ Saved to: {profile_file}")
        
        # Match
        print(f"  Matching...", end=' ')
        result = match_profile(profile, requirement, matcher)
        
        if not result:
            continue
        
        status = "✓ MATCH" if result.should_send_message else "✗ SKIP"
        print(f"{status} (Score: {result.score}/100)")
        
        # Auto-send if score high enough
        if result.score >= AUTO_SEND_THRESHOLD:
            send_message(profile, result.score, result.summary)
        
        # Store result
        results.append({
            'name': profile.name,
            'html_file': html_file,
            'profile_file': profile_file,
            'score': result.score,
            'should_send': result.should_send_message,
            'auto_sent': result.score >= AUTO_SEND_THRESHOLD,
            'summary': result.summary
        })
        
        processed_files.append(html_file)
    
    print()
    print("=" * 80)
    
    # 5. Summary
    print("PIPELINE SUMMARY")
    print("=" * 80)
    
    total = len(results)
    matches = sum(1 for r in results if r['should_send'])
    auto_sent = sum(1 for r in results if r['auto_sent'])
    
    print(f"\nProcessed: {total} profiles")
    print(f"Matches: {matches} ({matches/total*100:.1f}%)")
    print(f"Auto-sent: {auto_sent}")
    
    # Top candidates
    if matches > 0:
        print("\n" + "-" * 80)
        print("TOP CANDIDATES")
        print("-" * 80)
        
        top = sorted([r for r in results if r['should_send']], 
                    key=lambda x: x['score'], reverse=True)
        
        for i, r in enumerate(top, 1):
            sent_status = "📧 SENT" if r['auto_sent'] else "⏳ PENDING"
            print(f"\n{i}. {r['name']} - {r['score']}/100 - {sent_status}")
            print(f"   {r['summary'][:100]}...")
    
    # 6. Save results
    print("\n" + "=" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    result_file = f'{RESULTS_DIR}/pipeline_results_{timestamp}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'requirement': {
                'job_title': requirement.job_title,
                'company_name': requirement.company_name,
                'required_skills': requirement.required_skills
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Results saved: {result_file}")
    
    # 7. Move processed files
    processed_dir = os.path.join(RAW_HTML_DIR, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    for html_file in processed_files:
        src = os.path.join(RAW_HTML_DIR, html_file)
        dst = os.path.join(processed_dir, html_file)
        os.rename(src, dst)
    
    print(f"✓ Moved {len(processed_files)} files to: {processed_dir}")
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    process_pipeline()
