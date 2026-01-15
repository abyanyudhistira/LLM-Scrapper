"""
Main CLI - Single entry point untuk semua operasi
"""

import sys
import argparse
from scripts.pipeline import process_pipeline, MATCHING_MODE

def main():
    parser = argparse.ArgumentParser(
        description='LinkedIn Profile Matcher - Automated Recruitment System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py pipeline              # Run pipeline once
  python run.py pipeline --mode full  # Run with full LLM evaluation
  python run.py watch                 # Watch for new files
  python run.py match profile.json    # Match single profile
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run pipeline once')
    pipeline_parser.add_argument('--mode', choices=['fast', 'balanced', 'full'], 
                                default='fast', help='Matching mode (default: fast)')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch for new HTML files')
    watch_parser.add_argument('--interval', type=int, default=5, 
                             help='Check interval in seconds (default: 5)')
    watch_parser.add_argument('--mode', choices=['fast', 'balanced', 'full'], 
                             default='fast', help='Matching mode (default: fast)')
    
    # Match command
    match_parser = subparsers.add_parser('match', help='Match single profile')
    match_parser.add_argument('profile', help='Path to profile JSON file')
    match_parser.add_argument('--requirement', help='Path to requirement JSON file')
    match_parser.add_argument('--mode', choices=['fast', 'balanced', 'full'], 
                             default='fast', help='Matching mode (default: fast)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'pipeline':
        run_pipeline(args.mode)
    elif args.command == 'watch':
        run_watch(args.interval, args.mode)
    elif args.command == 'match':
        run_match(args.profile, args.requirement, args.mode)

def run_pipeline(mode='fast'):
    """Run pipeline once"""
    print(f"Running pipeline in {mode} mode...\n")
    
    # Update mode in pipeline
    from scripts import pipeline
    pipeline.MATCHING_MODE = mode
    
    process_pipeline()

def run_watch(interval=5, mode='fast'):
    """Watch for new files"""
    import time
    import os
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    
    # Update mode in pipeline
    from scripts import pipeline
    pipeline.MATCHING_MODE = mode
    
    class HTMLFileHandler(FileSystemEventHandler):
        def __init__(self):
            self.processing = False
        
        def on_created(self, event):
            if event.is_directory or not event.src_path.endswith('.html'):
                return
            
            print(f"\n✓ New file: {os.path.basename(event.src_path)}")
            time.sleep(2)  # Wait for file to be fully written
            
            if not self.processing:
                self.processing = True
                print("\n🚀 Triggering pipeline...")
                try:
                    process_pipeline()
                except Exception as e:
                    print(f"✗ Error: {e}")
                finally:
                    self.processing = False
    
    print("=" * 80)
    print("FILE WATCHER")
    print("=" * 80)
    print(f"\nWatching: data/raw_html")
    print(f"Mode: {mode}")
    print(f"Interval: {interval}s")
    print("Press Ctrl+C to stop\n")
    
    os.makedirs('data/raw_html', exist_ok=True)
    
    event_handler = HTMLFileHandler()
    observer = Observer()
    observer.schedule(event_handler, 'data/raw_html', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("✓ Stopped")

def run_match(profile_path, requirement_path=None, mode='fast'):
    """Match single profile"""
    import json
    from app.schemas.profile_schema import LinkedInProfile, Experience, Education
    from app.schemas.requirement_schema import JobRequirement
    from app.matcher.hybrid import get_hybrid_matcher
    
    print(f"Matching profile: {profile_path}\n")
    
    # Load profile
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile_data = json.load(f)
    
    profile = LinkedInProfile(
        name=profile_data['name'],
        headline=profile_data.get('headline', ''),
        experiences=[Experience(**exp) for exp in profile_data.get('experiences', [])],
        skills=profile_data.get('skills', []),
        education=[Education(**edu) for edu in profile_data.get('education', [])],
        total_experience_months=profile_data.get('total_experience_months', 0)
    )
    
    # Load requirement
    if requirement_path:
        with open(requirement_path, 'r', encoding='utf-8') as f:
            req_data = json.load(f)
        requirement = JobRequirement(**req_data)
    else:
        # Use default from pipeline
        from scripts.pipeline import JOB_TITLE, COMPANY_NAME, REQUIRED_SKILLS, MIN_EXPERIENCE_YEARS, PREFERRED_EDUCATION
        requirement = JobRequirement(
            job_title=JOB_TITLE,
            company_name=COMPANY_NAME,
            required_skills=REQUIRED_SKILLS,
            min_experience_years=MIN_EXPERIENCE_YEARS,
            preferred_education=PREFERRED_EDUCATION
        )
    
    # Initialize matcher
    if mode == 'fast':
        matcher = get_hybrid_matcher(use_embedding=False, use_llm=False)
    elif mode == 'balanced':
        matcher = get_hybrid_matcher(use_embedding=True, use_llm=False)
    else:
        matcher = get_hybrid_matcher(use_embedding=True, use_llm=True)
    
    # Match
    result = matcher.match(profile, requirement)
    
    # Display result
    print("=" * 80)
    print("MATCH RESULT")
    print("=" * 80)
    print(f"\nCandidate: {profile.name}")
    print(f"Position: {requirement.job_title}")
    print(f"Score: {result.score}/100")
    print(f"Decision: {'✓ SEND MESSAGE' if result.should_send_message else '✗ SKIP'}")
    print(f"\nSummary:\n{result.summary}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
