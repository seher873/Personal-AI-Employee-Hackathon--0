"""
Simple Facebook Post Test
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get credentials
token = os.getenv('FB_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')

if not token or not page_id:
    print("❌ Missing credentials in .env")
    exit()

print(f"📄 Posting to Page: {page_id}")

# Post to Facebook
url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
params = {
    'access_token': token,
    'message': 'Test post from AI Employee! 🤖 #AutoPost'
}

response = requests.post(url, params=params)
result = response.json()

if 'id' in result:
    print(f"✅ POST SUCCESSFUL!")
    print(f"   Post ID: {result['id']}")
    print(f"   View: https://facebook.com/{result['id'].split('_')[0]}")
else:
    print(f"❌ POST FAILED!")
    print(f"   Error: {result.get('error', {}).get('message', 'Unknown error')}")
