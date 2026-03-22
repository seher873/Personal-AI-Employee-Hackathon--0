"""
Find Facebook Page ID and Instagram ID for: urojk77
App ID: 781070051729264
"""

import os
import sys
import requests
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FB_ACCESS_TOKEN

print("=" * 60)
print("Finding Page & Instagram IDs for: urojk77")
print("App ID: 781070051729264")
print("=" * 60)

# Step 1: Get user info
print("\n[Step 1] Getting user info...")
url = "https://graph.facebook.com/me"
params = {
    'access_token': FB_ACCESS_TOKEN,
    'fields': 'id,name,email'
}
response = requests.get(url, params=params)

if response.status_code == 200:
    user = response.json()
    print(f"User ID: {user.get('id')}")
    print(f"Name: {user.get('name')}")
    user_id = user.get('id')
else:
    print(f"Error: {response.text}")
    print("\nToken is invalid or expired!")
    print("Get new token from: https://developers.facebook.com/tools/explorer/")
    sys.exit(1)

# Step 2: Get Pages with page_token
print("\n[Step 2] Fetching your Facebook Pages...")
url = f"https://graph.facebook.com/v18.0/{user_id}/accounts"
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
        
        # Check Instagram
        if page.get('instagram_business_account'):
            ig_id = page['instagram_business_account']['id']
            print(f"\nInstagram ID: {ig_id}")
            
            # Get Instagram details
            ig_url = f"https://graph.facebook.com/v18.0/{ig_id}"
            ig_params = {
                'access_token': page_token,  # Use page token for IG
                'fields': 'username,name,biography,followers_count,profile_picture_url'
            }
            ig_response = requests.get(ig_url, params=ig_params)
            
            if ig_response.status_code == 200:
                ig_details = ig_response.json()
                print(f"Username: @{ig_details.get('username', 'N/A')}")
                print(f"Name: {ig_details.get('name', 'N/A')}")
                print(f"Followers: {ig_details.get('followers_count', 'N/A')}")
        else:
            print("\nNo Instagram Business account connected")
            print("To add Instagram:")
            print("1. Convert Instagram to Business account")
            print("2. Connect it to this Facebook Page")
            print("3. Visit: https://www.facebook.com/accounts/")
        
        print()
    
    # Save config suggestion
    print("\n" + "=" * 60)
    print("READY TO UPDATE .env!")
    print("=" * 60)
    
    if len(pages) > 0:
        page = pages[0]
        print("\nCopy these values to .env file:\n")
        print(f"FB_ACCESS_TOKEN={page.get('access_token', '')}")
        print(f"FB_PAGE_ID={page.get('id', '')}")
        
        if page.get('instagram_business_account'):
            print(f"IG_ID={page['instagram_business_account']['id']}")
        else:
            print("IG_ID=(connect Instagram to Page first)")
        
        print("\n" + "=" * 60)
        print("IMPORTANT: Use the PAGE ACCESS TOKEN (not user token)!")
        print("=" * 60)

elif response.status_code == 200:
    print("\nNo Pages found!")
    print("\nPossible reasons:")
    print("1. You don't have admin access to any Facebook Page")
    print("2. Token doesn't have 'pages_show_list' permission")
    print("\nSolution:")
    print("1. Create a Facebook Page: https://facebook.com/pages/create")
    print("2. Or get token with proper permissions from Graph Explorer")
else:
    print(f"\nError: {pages_data}")
    if 'error' in pages_data:
        print(f"Error message: {pages_data['error'].get('message')}")

print("\n" + "=" * 60)
