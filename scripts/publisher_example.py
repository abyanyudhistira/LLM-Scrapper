"""
Example Publisher Script - For scraper to publish raw profiles to queue

UPDATED: Menggunakan actual database schema
- scraped_leads table
- search_templates table
"""

import json
from datetime import datetime
from app.utils.rabbitmq_client import get_rabbitmq_client


def publish_profile(html_content: str, template_id: str, lead_id: str, matching_mode: str = 'balanced'):
    """
    Publish a scraped profile to RabbitMQ queue
    
    Args:
        html_content: Raw HTML from LinkedIn profile
        template_id: Template ID from 'search_templates' table
        lead_id: Lead ID from 'scraped_leads' table
        matching_mode: 'fast', 'balanced', or 'full'
    """
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'lead_id': lead_id,
        'template_id': template_id,
        'html_content': html_content,
        'matching_mode': matching_mode,
        'scraped_at': datetime.now().isoformat()
    }
    
    rabbitmq.publish(message)
    print(f"✓ Published lead {lead_id} to queue")


def publish_batch(profiles: list):
    """
    Publish multiple profiles at once
    
    Args:
        profiles: List of dicts with keys: html_content, template_id, lead_id, matching_mode
    """
    rabbitmq = get_rabbitmq_client()
    
    for profile in profiles:
        message = {
            'lead_id': profile['lead_id'],
            'template_id': profile['template_id'],
            'html_content': profile['html_content'],
            'matching_mode': profile.get('matching_mode', 'balanced'),
            'scraped_at': datetime.now().isoformat()
        }
        
        rabbitmq.publish(message)
        print(f"✓ Published lead {profile['lead_id']}")
    
    print(f"\n✓ Published {len(profiles)} profiles to queue")


# Example usage
if __name__ == "__main__":
    # Example 1: Publish single profile
    example_html = """
    <html>
        <body>
            <h1>John Doe</h1>
            <p>Senior Software Engineer at Tech Corp</p>
            <!-- ... rest of LinkedIn HTML ... -->
        </body>
    </html>
    """
    
    publish_profile(
        html_content=example_html,
        template_id='template-uuid-from-search-templates-table',
        lead_id='lead-uuid-from-scraped-leads-table',
        matching_mode='balanced'
    )
    
    # Example 2: Publish batch
    # profiles_batch = [
    #     {
    #         'lead_id': 'lead-001',
    #         'template_id': 'template-123',
    #         'html_content': '<html>...</html>',
    #         'matching_mode': 'fast'
    #     },
    #     {
    #         'lead_id': 'lead-002',
    #         'template_id': 'template-123',
    #         'html_content': '<html>...</html>',
    #         'matching_mode': 'balanced'
    #     }
    # ]
    # publish_batch(profiles_batch)
