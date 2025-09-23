import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('WHATSAPP_ACCESS_TOKEN')
phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

# Test the token
url = f"https://graph.facebook.com/v18.0/{phone_id}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
print(f"Token Test Response: {response.status_code}")
print(f"Response: {response.json()}")

# Try sending a test message
send_url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
test_message = {
    "messaging_product": "whatsapp",
    "to": "917019567529",  # Your number
    "type": "text",
    "text": {"body": "Test message - Token verification"}
}

send_response = requests.post(send_url, json=test_message, headers=headers)
print(f"\nSend Test Response: {send_response.status_code}")
print(f"Response: {send_response.json()}")