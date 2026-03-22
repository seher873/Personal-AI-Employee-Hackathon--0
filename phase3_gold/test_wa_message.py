"""
Simple WhatsApp Test Message
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get credentials
phone_id = os.getenv('WHATSAPP_PHONE')
token = os.getenv('WHATSAPP_API_KEY')

if not phone_id or not token:
    print("❌ Missing WhatsApp credentials in .env")
    exit()

print(f"📱 WhatsApp Test")
print(f"   Phone ID: {phone_id}")

# Your number (add country code, no + sign)
test_number = "923283490851"  # Pakistan: 92 + 3283490851

print(f"   Sending to: {test_number}")

# Send message
url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
data = {
    'messaging_product': 'whatsapp',
    'to': test_number,
    'type': 'text',
    'text': {
        'body': 'Hello from AI Employee! 🤖\n\nWhatsApp connection test successful!'
    }
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if 'messages' in result:
    print(f"\n✅ MESSAGE SENT!")
    print(f"   Message ID: {result['messages'][0]['id']}")
    print(f"   Check your WhatsApp: +{test_number}")
else:
    print(f"\n❌ FAILED!")
    print(f"   Error: {result.get('error', {}).get('message', 'Unknown error')}")
    print("\n💡 Note: You can only send to verified test numbers initially.")
    print("   Add your number in WhatsApp Dashboard → API Setup → Add Test Number")
