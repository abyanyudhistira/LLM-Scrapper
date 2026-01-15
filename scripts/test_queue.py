"""
Test Queue Script - Test RabbitMQ and Supabase connection
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.rabbitmq_client import get_rabbitmq_client
from app.utils.supabase_client import get_supabase_client
import json


def test_rabbitmq():
    """Test RabbitMQ connection"""
    print("\n" + "="*60)
    print("TESTING RABBITMQ CONNECTION")
    print("="*60)
    
    try:
        rabbitmq = get_rabbitmq_client()
        queue_size = rabbitmq.get_queue_size()
        print(f"✓ Connected to RabbitMQ")
        print(f"✓ Queue size: {queue_size} messages")
        return True
    except Exception as e:
        print(f"✗ RabbitMQ connection failed: {e}")
        return False


def test_supabase():
    """Test Supabase connection"""
    print("\n" + "="*60)
    print("TESTING SUPABASE CONNECTION")
    print("="*60)
    
    try:
        supabase = get_supabase_client()
        
        # Test getting companies
        companies = supabase.get_all_companies()
        print(f"✓ Connected to Supabase")
        print(f"✓ Companies: {len(companies)}")
        
        if companies:
            print("\nCompanies:")
            for company in companies:
                print(f"  - {company.get('name')} (code: {company.get('code')})")
        
        return True
    except Exception as e:
        print(f"✗ Supabase connection failed: {e}")
        return False


def publish_test_message():
    """Publish a test message to queue"""
    print("\n" + "="*60)
    print("PUBLISHING TEST MESSAGE")
    print("="*60)
    
    try:
        rabbitmq = get_rabbitmq_client()
        
        test_message = {
            'lead_id': 'test-lead-001',
            'template_id': 'test-template-001',
            'html_content': '<html><body><h1>Test Profile</h1></body></html>',
            'matching_mode': 'fast'
        }
        
        rabbitmq.publish(test_message)
        print(f"✓ Published test message")
        print(f"  Lead ID: {test_message['lead_id']}")
        print(f"  Template ID: {test_message['template_id']}")
        
        queue_size = rabbitmq.get_queue_size()
        print(f"✓ Queue size after publish: {queue_size} messages")
        
        return True
    except Exception as e:
        print(f"✗ Failed to publish test message: {e}")
        return False


def main():
    """Run all tests"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                    QUEUE & DATABASE TEST                       ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'rabbitmq': test_rabbitmq(),
        'supabase': test_supabase()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"RabbitMQ: {'✓ PASS' if results['rabbitmq'] else '✗ FAIL'}")
    print(f"Supabase: {'✓ PASS' if results['supabase'] else '✗ FAIL'}")
    
    if all(results.values()):
        print("\n✓ All tests passed!")
        
        # Ask if user wants to publish test message
        response = input("\nPublish a test message to queue? (y/n): ")
        if response.lower() == 'y':
            publish_test_message()
    else:
        print("\n✗ Some tests failed. Please check your configuration.")
        print("\nMake sure:")
        print("1. RabbitMQ is running (docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management)")
        print("2. .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("3. Supabase tables are created (run scripts/setup_supabase.sql)")


if __name__ == "__main__":
    main()
