"""
Simple Test - Publish via Docker Exec
"""

import subprocess
import uuid

# Test HTML
test_html = """
<html>
<body>
    <h1>John Doe</h1>
    <p>Senior Backend Developer at Tech Corp</p>
    <p>Skills: Python, Django, PostgreSQL, Docker</p>
    <p>Experience: 5 years</p>
</body>
</html>
"""

lead_id = str(uuid.uuid4())
template_id = 'test-template-' + str(uuid.uuid4())[:8]

print("="*60)
print("PUBLISHING TEST MESSAGE")
print("="*60)
print(f"Lead ID: {lead_id}")
print(f"Template ID: {template_id}")
print("")

# Create Python command to run inside container
python_code = f"""
import json
from app.utils.rabbitmq_client import get_rabbitmq_client

message = {{
    'lead_id': '{lead_id}',
    'template_id': '{template_id}',
    'html_content': '''{test_html}''',
    'matching_mode': 'fast'
}}

rabbitmq = get_rabbitmq_client()
rabbitmq.publish(message)
print('✓ Message published!')
print(f'Queue size: {{rabbitmq.get_queue_size()}}')
"""

# Run inside worker container
cmd = ['docker', 'exec', 'worker-1', 'python', '-c', python_code]

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
    
    print("")
    print("="*60)
    print("NEXT: Watch worker logs")
    print("="*60)
    print("docker-compose logs -f worker")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure worker container is running:")
    print("docker-compose ps")
