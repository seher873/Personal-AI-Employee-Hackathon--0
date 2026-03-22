"""
Debug Token - Check what the token can access
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
print("Token Debug Tool")
print("=" * 60)

# Step 1: Debug the token itself
print("\n1. Checking token info...")
url = "https://graph.facebook.com/me"
params = {'access_token': FB_ACCESS_TOKEN}

response = requests.get(url, params=params)
print(f"Response: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Token Info: {data}")
    
    # Get user ID
    user_id = data.get('id')
    print(f"\n2. User ID: {user_id}")
    
    # Get user accounts
    print("\n3. Fetching user accounts/pages...")
    url = f"https://graph.facebook.com/v18.0/{user_id}/accounts"
    params = {'access_token': FB_ACCESS_TOKEN}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        pages = response.json()
        print(f"✅ Pages: {pages}")
        
        if 'data' in pages and len(pages['data']) > 0:
            print("\n4. Your Pages:")
            for page in pages['data']:
                print(f"   - Name: {page.get('name')}")
                print(f"     ID: {page.get('id')}")
                print(f"     Access Token: {page.get('access_token', 'N/A')[:30]}...")
                print()
    else:
        print(f"❌ Error fetching pages: {response.text}")
    
    # Get Instagram accounts
    print("\n5. Fetching Instagram accounts...")
    url = f"https://graph.facebook.com/v18.0/{user_id}/instagram_business_accounts"
    params = {'access_token': FB_ACCESS_TOKEN}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        ig_accounts = response.json()
        print(f"✅ Instagram Accounts: {ig_accounts}")
        
        if 'data' in ig_accounts and len(ig_accounts['data']) > 0:
            print("\n6. Your Instagram Business Accounts:")
            for ig in ig_accounts['data']:
                ig_id = ig.get('id')
                print(f"   - ID: {ig_id}")
                
                # Get more details
                url = f"https://graph.facebook.com/v18.0/{ig_id}"
                params = {'access_token': FB_ACCESS_TOKEN, 'fields': 'username,biography,followers_count'}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    ig_details = response.json()
                    print(f"     Username: {ig_details.get('username', 'N/A')}")
                    print(f"     Followers: {ig_details.get('followers_count', 'N/A')}")
    else:
        print(f"❌ Error fetching Instagram: {response.text}")
else:
    print(f"❌ Token error: {response.text}")

print("\n" + "=" * 60)
print("Debug complete!")
print("=" * 60)
