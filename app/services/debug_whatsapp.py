"""
WhatsApp Cloud API Debugging Script
----------------------------------
Run this file to diagnose why messages are not being sent/received.
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load env vars directly (adjust if you use dotenv or settings module)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "your-token-here")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "742954942242352")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "healthcare_bot_verify_secure_123")

BASE_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}"
HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}


async def check_token():
    """Check if token and phone number ID are valid"""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=HEADERS)
        print("\n🔍 TOKEN VALIDATION")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")


async def send_test_message():
    """Send a test WhatsApp message"""
    url = f"{BASE_URL}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": "917019567529",  # ✅ your number without +
        "text": {"body": "🧪 Debug test message from Healthcare Chatbot"},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=HEADERS, json=payload)
        print("\n📤 TEST MESSAGE SEND")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")


async def main():
    print("🚑 Running WhatsApp Debugging Script")
    print("=" * 50)

    # 1. Check env variables
    print("\n📌 ENV VARIABLES CHECK")
    print(f"Phone Number ID: {PHONE_NUMBER_ID}")
    print(f"Token present: {bool(WHATSAPP_TOKEN)}")
    print(f"Token prefix: {WHATSAPP_TOKEN[:15]}...")

    # 2. Validate token
    await check_token()

    # 3. Try sending test message
    await send_test_message()

    print("\n✅ Debugging finished. If token & send test fail -> recheck .env")


if __name__ == "__main__":
    asyncio.run(main())
