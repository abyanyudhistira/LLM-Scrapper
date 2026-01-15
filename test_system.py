"""
Complete System Test
Run: python test_system.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.utils.rabbitmq_client import get_rabbitmq_client
import uuid

def test_publish():
    """Test publish message to queue"""
    print("\n" + "="*60)
    print("TEST: PUBLISH MESSAGE TO QUEUE")
    print("="*60)
    
    # Sample LinkedIn HTML
    test_html = """
    <html>
    <body>
        <div class="profile">
            <h1>John Doe</h1>
            <p class="headline">Senior Backend Developer at Tech Corp</p>
            
            <div class="experience">
                <h3>Senior Backend Developer</h3>
                <p>Tech Corp | 2020 - Present (3 years)</p>
                <p>Developed scalable APIs using Python and Django</p>
            </div>
            
            <div class="experience">
                <h3>Backend Developer</h3>
                <p>StartupXYZ | 2018 - 2020 (2 years)</p>
                <p>Built microservices with Flask and PostgreSQL</p>
            </div>
            
            <div class="skills">
                <span>Python</span>
                <span>Django</span>
                <span>PostgreSQL</span>
                <span>Docker</span>
                <span>REST API</span>
                <span>Git</span>
            </div>
            
            <div class="education">
                <h3>Bachelor of Computer Science</h3>
                <p>University of Technology | 2014 - 2018</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        rabbitmq = get_rabbitmq_client()
        
        lead_id = str(uuid.uuid4())
        template_id = 'test-template-' + str(uuid.uuid4())[:8]
        
        message = {
            'lead_id': lead_id,
            'template_id': template_id,
            'html_content': test_html,
            'matching_mode': 'fast'
        }
        
        print(f"\nPublishing test message...")
        print(f"  Lead ID: {lead_id}")
        print(f"  Template ID: {template_id}")
        print(f"  Mode: fast")
        
        rabbitmq.publish(message)
        
        print(f"\n✓ Message published successfully!")
        
        queue_size = rabbitmq.get_queue_size()
        print(f"✓ Queue size: {queue_size} message(s)")
        
        print(f"\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Check worker logs:")
        print("   docker-compose logs -f worker")
        print("")
        print("2. Worker will process the message and you'll see:")
        print("   - Extracting profile data...")
        print("   - Loading job requirement...")
        print("   - Matching profile...")
        print("   - Saving results...")
        print("")
        print("3. Check results in Supabase:")
        print(f"   SELECT * FROM scraped_leads WHERE id = '{lead_id}';")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                    SYSTEM TEST                                 ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    test_publish()
