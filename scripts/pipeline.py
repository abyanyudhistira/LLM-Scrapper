di"""
Simplified Pipeline: Scraper → Cleaner → Matcher → Sender
"""

from app.schemas.profile_schema import LinkedInProfile, Experience, Education
from app.schemas.requirement_schema import JobRequirement
from app.matcher.hybrid import get_hybrid_matcher
from app.utils.html_cleaner import clean_html
from app.utils.config import AUTO_SEND_THRESHOLD
from app.llm.gemini_client import GeminiClient
from app.llm.prompt import create_extraction_prompt
import json
import os
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
RAW_HTML_DIR = 'data/raw_html'
PROFILES_DIR = 'data/profiles'
RESULTS_DIR = 'data/results'

# ============================================================================

def extract_profile_from_html(html_content: str) -> dict:
    """Extract profile data from HTML using html_cleaner and LLM"""
    # Clean HTML to plain text
    cleaned_text = clean_html(html_content)
    
    # Use LLM to extract structured data
    client = GeminiClient()
    prompt = create_extraction_prompt(cleaned_text)
    
    try:
        response = client.generate_content(prompt)
        # Parse JSON response
        profile_data = json.loads(response)
        return profile_data
    except Exception as e:
        print(f"    ✗ Extraction failed: {e}")
        return None

def save_profile(profile, filename):
    """Save profile to JSON"""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    safe_name = profile.name.replace(' ', '_').replace('/', '_')
    output_file = f'{PROFILES_DIR}/{safe_name}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(profile.model_dump_json(indent=2))
    
    return output_file

def send_message(profile, score, summary):
    """Send message to candidate (placeholder)"""
    print(f"    📧 Sending message to {profile.name}...")
    
    # TODO: Implement actual message sending
    message = f"""
    Hi {profile.name},
    
    Kami tertarik dengan profile Anda untuk posisi {JOB_TITLE}.
    
    {summary}
    
    Apakah Anda tertarik untuk diskusi lebih lanjut?
    """
    
    print(f"    ✓ Message sent! (Score: {score}/100)")
    return True

def process_pipeline():
    """Main pipeline"""
    
    print("=" * 80)
    print("AUTOMATED PIPELINE")
    print("=" * 80)
    print()
    
    # 1. Check for HTML files
    print("1. Checking for new profiles...")
    
    if not os.path.exists(RAW_HTML_DIR):
        os.makedirs(RAW_HTML_DIR)
        print(f"   Created: {RAW_HTML_DIR}")
        print(f"   Place HTML files from scraper here")
        return
    
    html_files = [f for f in os.listdir(RAW_HTML_DIR) if f.endswith('.html')]
    
    if not html_files:
        print(f"   No HTML files found")
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
    
    # 4. Process files
    print("4. Processing profiles...")
    print("-" * 80)
    
    results = []
    processed_files = []
    
    for i, html_file in enumerate(html_files, 1):
        print(f"\n[{i}/{len(html_files)}] {html_file}")
        
        html_path = os.path.join(RAW_HTML_DIR, html_file)
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean & Extract using html_cleaner + LLM
        print(f"  Cleaning & extracting...", end=' ')
        profile_data = extract_profile_from_html(html_content)
        
        if not profile_data:
            print("✗ Failed")
            continue
        
        # Create profile
        profile = LinkedInProfile(
            name=profile_data.get('name', 'Unknown'),
            headline=profile_data.get('headline', ''),
            experiences=[Experience(**exp) for exp in profile_data.get('experiences', [])],
            skills=profile_data.get('skills', []),
            education=[Education(**edu) for edu in profile_data.get('education', [])],
            total_experience_months=profile_data.get('total_experience_months', 0)
        )
        print(f"✓ {profile.name}")
        
        # Save profile
        profile_file = save_profile(profile, html_file)
        print(f"  ✓ Saved: {profile_file}")
        
        # Match
        print(f"  Matching...", end=' ')
        try:
            result = matcher.match(profile, requirement)
            status = "✓ MATCH" if result.should_send_message else "✗ SKIP"
            print(f"{status} (Score: {result.score}/100)")
            
            # Auto-send
            if result.score >= AUTO_SEND_THRESHOLD:
                send_message(profile, result.score, result.summary)
            
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
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    print("=" * 80)
    
    # 5. Summary
    print("PIPELINE SUMMARY")
    print("=" * 80)
    
    total = len(results)
    if total == 0:
        print("\nNo profiles processed")
        return
    
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
    
    result_file = f'{RESULTS_DIR}/pipeline_{timestamp}.json'
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
