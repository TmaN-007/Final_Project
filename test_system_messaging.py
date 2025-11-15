"""Test system messaging functionality"""

import sys
sys.path.insert(0, '/Users/hii/Desktop/AiDD Final Project/Final_Project')

from src.utils import system_messaging

# Test sending a system message to user 2
print("Testing system messaging...")
print(f"System user ID: {system_messaging.SYSTEM_USER_ID}")

result = system_messaging.send_system_message(
    recipient_id=2,
    subject="Test Message from System",
    content="This is a test message to verify system messaging is working correctly.",
    resource_id=4
)

print(f"Result: {result}")

if result:
    print("SUCCESS: Message sent!")
else:
    print("FAILED: Message was not sent")
