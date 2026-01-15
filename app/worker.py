"""
RabbitMQ Worker - Consumes messages and processes profiles
Menggunakan existing database schema
"""

import json
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from app.utils.rabbitmq_client import get_rabbitmq_client
from app.utils.supabase_client import get_supabase_client
from app.utils.html_cleaner import clean_html
from app.llm.gemini_client import GeminiClient
from app.llm.prompt import create_extraction_prompt
from app.matcher.hybrid import get_hybrid_matcher
from app.schemas.profile_schema import LinkedInProfile, Experience, Education
from app.schemas.requirement_schema import JobRequirement
from app.utils.config import MATCH_THRESHOLD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfileWorker:
    """Worker to process profile messages from RabbitMQ"""
    
    def __init__(self):
        self.rabbitmq = get_rabbitmq_client()
        self.supabase = get_supabase_client()
        self.gemini = GeminiClient()
        self.matcher = None  # Will be initialized per job
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_profile_from_html(self, html_content: str) -> dict:
        """Extract profile data from HTML using html_cleaner and LLM"""
        # Clean HTML to plain text
        cleaned_text = clean_html(html_content)
        
        # Use LLM to extract structured data
        prompt = create_extraction_prompt(cleaned_text)
        response = self.gemini.generate_content(prompt)
        
        # Parse JSON response
        profile_data = json.loads(response)
        return profile_data
    
    def create_profile_object(self, profile_data: dict) -> LinkedInProfile:
        """Create LinkedInProfile object from extracted data"""
        return LinkedInProfile(
            name=profile_data.get('name', 'Unknown'),
            headline=profile_data.get('headline', ''),
            experiences=[Experience(**exp) for exp in profile_data.get('experiences', [])],
            skills=profile_data.get('skills', []),
            education=[Education(**edu) for edu in profile_data.get('education', [])],
            total_experience_months=profile_data.get('total_experience_months', 0)
        )
    
    def get_job_requirement_from_template(self, template_id: str) -> JobRequirement:
        """
        Get job requirement from search_template
        Parse dari job_title dan note field
        """
        template = self.supabase.get_template_with_company(template_id)
        
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Get company info
        company = template.get('companies', {})
        company_name = company.get('name', 'Unknown Company')
        
        # Parse job requirements dari template
        job_title = template.get('job_title', '')
        note = template.get('note', '')
        
        # Default requirements (bisa di-customize)
        # TODO: Bisa parse dari 'note' field atau add JSONB field 'requirements'
        return JobRequirement(
            job_title=job_title,
            company_name=company_name,
            required_skills=['Python', 'Backend'],  # Default, bisa di-customize
            min_experience_years=2,
            preferred_education=['Sarjana'],
            job_description=note,
            nice_to_have_skills=[]
        )
    
    def initialize_matcher(self, matching_mode: str = 'balanced'):
        """Initialize matcher based on mode"""
        if matching_mode == 'fast':
            self.matcher = get_hybrid_matcher(use_embedding=False, use_llm=False)
        elif matching_mode == 'balanced':
            self.matcher = get_hybrid_matcher(use_embedding=True, use_llm=False)
        else:  # full
            self.matcher = get_hybrid_matcher(use_embedding=True, use_llm=True)
    
    def process_message(self, ch, method, properties, body):
        """
        Process a single message from queue
        
        Message format:
        {
            "lead_id": "uuid",
            "template_id": "uuid",
            "html_content": "raw html string",
            "matching_mode": "fast|balanced|full"
        }
        """
        lead_id = None
        
        try:
            # Parse message
            message = json.loads(body)
            lead_id = message.get('lead_id')
            template_id = message.get('template_id')
            html_content = message.get('html_content')
            matching_mode = message.get('matching_mode', 'balanced')
            
            logger.info(f"Processing lead: {lead_id}")
            
            # Step 1: Extract profile from HTML
            logger.info(f"  Extracting profile data...")
            profile_data = self.extract_profile_from_html(html_content)
            profile = self.create_profile_object(profile_data)
            logger.info(f"  ✓ Extracted: {profile.name}")
            
            # Step 2: Get job requirement from template
            logger.info(f"  Loading job requirement...")
            requirement = self.get_job_requirement_from_template(template_id)
            logger.info(f"  ✓ Job: {requirement.job_title} at {requirement.company_name}")
            
            # Step 3: Initialize matcher
            if not self.matcher:
                logger.info(f"  Initializing matcher ({matching_mode})...")
                self.initialize_matcher(matching_mode)
            
            # Step 4: Match profile
            logger.info(f"  Matching profile...")
            result = self.matcher.match(profile, requirement)
            logger.info(f"  ✓ Score: {result.score}/100")
            
            # Step 5: Update scraped_leads table
            logger.info(f"  Saving results...")
            
            # Prepare profile_data untuk save
            full_profile_data = {
                'extracted_profile': profile.model_dump(),
                'match_result': {
                    'score': result.score,
                    'summary': result.summary,
                    'breakdown': result.breakdown,
                    'should_send_message': result.should_send_message
                },
                'matching_mode': matching_mode,
                'processed_at': datetime.now().isoformat()
            }
            
            self.supabase.update_lead_score(
                lead_id=lead_id,
                score=result.score,
                profile_data=full_profile_data
            )
            logger.info(f"  ✓ Updated lead score")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            logger.info(f"✓ Completed: {profile.name} - Score: {result.score}/100")
            
        except Exception as e:
            logger.error(f"✗ Error processing lead {lead_id}: {e}", exc_info=True)
            
            # Reject message (will be requeued or sent to DLQ)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start(self):
        """Start consuming messages"""
        logger.info("=" * 80)
        logger.info("PROFILE WORKER STARTED")
        logger.info("=" * 80)
        logger.info(f"Queue: {self.rabbitmq.channel.queue_declare(queue='raw_profiles_queue', passive=True).method.queue}")
        logger.info("Waiting for messages...")
        logger.info("=" * 80)
        
        try:
            self.rabbitmq.consume(self.process_message)
        except KeyboardInterrupt:
            logger.info("\nShutting down worker...")
            self.rabbitmq.stop()
        except Exception as e:
            logger.error(f"Worker error: {e}")
            self.rabbitmq.stop()
            raise


def main():
    """Main entry point"""
    worker = ProfileWorker()
    worker.start()


if __name__ == "__main__":
    main()
