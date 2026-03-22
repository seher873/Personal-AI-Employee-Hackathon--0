"""
Fetch Facebook Pages and Instagram Accounts
Run this to get your correct Page ID and Instagram ID
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
print("Facebook Pages & Instagram Account Finder")
print("=" * 60)

# Get user ID first
print("\n1. Getting user info...")
url = "https://graph.facebook.com/me"
params = {'access_token': FB_ACCESS_TOKEN}
response = requests.get(url, params=params)

if response.status_code != 200:
    print(f"Error: {response.text}")
    print("\nToken is invalid. Please get a new token from:")
    print("https://developers.facebook.com/tools/explorer/")
    sys.exit(1)

user_data = response.json()
user_id = user_data.get('id')
print(f"User ID: {user_id}")
print(f"Name: {user_data.get('name')}")

# Get Pages
print("\n2. Fetching your Facebook Pages...")
url = f"https://graph.facebook.com/v18.0/{user_id}/accounts"
params = {'access_token': FB_ACCESS_TOKEN}
response = requests.get(url, params=params)

pages_data = response.json()

if response.status_code == 200 and pages_data.get('data'):
    pages = pages_data['data']
    print(f"Found {len(pages)} Page(s):\n")
    
    for i, page in enumerate(pages, 1):
        page_id = page.get('id')
        page_name = page.get('name')
        page_token = page.get('access_token', '')
        
        print(f"[{i}] Page: {page_name}")
        print(f"    ID: {page_id}")
        print(f"    Token: {page_token[:40]}...")
        
        # Try to get Instagram account for this page
        print(f"    Checking Instagram...")
        ig_url = f"https://graph.facebook.com/v18.0/{page_id}"
        ig_params = {
            'access_token': FB_ACCESS_TOKEN,
            'fields': 'instagram_business_account'
        }
        ig_response = requests.get(ig_url, params=ig_params)
        
        if ig_response.status_code == 200:
            ig_data = ig_response.json()
            if ig_data.get('instagram_business_account'):
                ig_id = ig_data['instagram_business_account']['id']
                print(f"    Instagram ID: {ig_id}")
                
                # Get Instagram details
                ig_details_url = f"https://graph.facebook.com/v18.0/{ig_id}"
                ig_details_params = {
                    'access_token': FB_ACCESS_TOKEN,
                    'fields': 'username,name,biography,followers_count'
                }
                ig_details_response = requests.get(ig_details_url, params=ig_details_params)
                
                if ig_details_response.status_code == 200:
                    ig_details = ig_details_response.json()
                    print(f"    Username: @{ig_details.get('username', 'N/A')}")
                    print(f"    Followers: {ig_details.get('followers_count', 'N/A')}")
            else:
                print(f"    No Instagram Business account connected")
        print()
    
    # Save to file for easy copy
    print("\n3. Ready to update .env file!")
    print("\nCopy the Page ID and Instagram ID from above")
    print("Then update your .env file:")
    print(f"   FB_PAGE_ID=<paste page id here>")
    print(f"   IG_ID=<paste instagram id here>")
    
else:
    print("No pages found!")
    print("\nPossible reasons:")
    print("1. You don't have any Facebook Pages")
    print("2. Token doesn't have 'pages_show_list' permission")
    print("\nGet a new token with these permissions:")
    print("- pages_manage_posts")
    print("- pages_read_engagement")
    print("- pages_show_list")
    print("- instagram_basic")
    print("- instagram_content_publish")

print("\n" + "=" * 60)
