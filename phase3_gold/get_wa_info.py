"""
Get WhatsApp Business Account Info
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('WHATSAPP_API_KEY')

if not token:
    print("❌ Missing WHATSAPP_API_KEY in .env")
    exit()

print("🔍 Getting WhatsApp Business Account Info...")

url = 'https://graph.facebook.com/v18.0/me/whatsapp_business_accounts'
params = {'access_token': token}

response = requests.get(url, params=params)
result = response.json()

print(result)

if 'data' in result and len(result['data']) > 0:
    print("\n✅ Found WhatsApp Business Account!")
    for account in result['data']:
        print(f"   ID: {account.get('id', 'Unknown')}")
        print(f"   Name: {account.get('name', 'Unknown')}")
else:
    print("\n❌ No WhatsApp Business Account found!")
    print("   Error:", result.get('error', {}).get('message', 'Unknown'))
