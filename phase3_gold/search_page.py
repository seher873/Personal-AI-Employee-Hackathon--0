"""
Search for Page: uroj's online page
"""

import os
import sys
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FB_ACCESS_TOKEN

print("=" * 60)
print("Searching for Page: uroj's online page")
print("=" * 60)

# Search for page by name
print("\n[Step 1] Searching for page by name...")
search_url = "https://graph.facebook.com/v18.0/search"
search_params = {
    'type': 'page',
    'q': "uroj's online page",
    'access_token': FB_ACCESS_TOKEN
}

response = requests.get(search_url, params=search_params)
search_data = response.json()

if response.status_code == 200 and search_data.get('data'):
    pages = search_data['data']
    print(f"Found {len(pages)} page(s):\n")
    
    for i, page in enumerate(pages, 1):
        page_id = page.get('id')
        page_name = page.get('name')
        print(f"[{i}] {page_name}")
        print(f"    ID: {page_id}")
        print()
else:
    print("Page not found in search")
    print("\nTrying to get user pages again...")

# Get user ID
print("\n[Step 2] Getting user pages with expanded permissions...")
url = "https://graph.facebook.com/me"
params = {'access_token': FB_ACCESS_TOKEN}
response = requests.get(url, params=params)
user = response.json()
user_id = user.get('id')

# Try different API version
url = f"https://graph.facebook.com/v17.0/{user_id}/accounts"
params = {
    'access_token': FB_ACCESS_TOKEN,
    'fields': 'id,name,access_token,instagram_business_account'
}
response = requests.get(url, params=params)
pages_data = response.json()

if response.status_code == 200 and pages_data.get('data'):
    pages = pages_data['data']
    print(f"Found {len(pages)} Page(s):\n")
    
    for i, page in enumerate(pages, 1):
        page_id = page.get('id')
        page_name = page.get('name')
        page_token = page.get('access_token', '')
        
        print(f"{'='*50}")
        print(f"PAGE #{i}")
        print(f"{'='*50}")
        print(f"Name: {page_name}")
        print(f"ID: {page_id}")
        print(f"Access Token: {page_token[:50]}...")
        
        if page.get('instagram_business_account'):
            ig_id = page['instagram_business_account']['id']
            print(f"\nInstagram ID: {ig_id}")
        else:
            print("\nNo Instagram connected")
        print()
else:
    print("\nStill no pages found!")
    print("\n" + "=" * 60)
    print("ACTION REQUIRED")
    print("=" * 60)
    print("""
Your current token doesn't have Page permissions.

DO THIS NOW:
------------
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app: 781070051729264
3. Click "Get Token" → "Get Page Access Token"
4. Select "uroj's online page" from the list
5. Copy the NEW token (Page Access Token)
6. Copy the Page ID
7. Share with me!

The token you're using is a USER token, not a PAGE token.
You need PAGE Access Token for posting to Facebook Pages.
""")

print("=" * 60)
