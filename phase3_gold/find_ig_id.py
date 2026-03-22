#!/usr/bin/env python3
"""
Try different API calls to find Instagram Business Account ID
"""
import requests
from config import FB_ACCESS_TOKEN

def find_ig_account():
    print("Trying multiple API approaches to find your Instagram Business Account ID...")

    # Approach 1: Using me/accounts with proper fields
    print("\n1. Trying /me/accounts with fields parameter...")
    try:
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}&fields=id,name,access_token,instagram_business_account"
        response = requests.get(url)
        print(f"   Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"   Found {len(pages)} pages")
            for i, page in enumerate(pages):
                ig_account = page.get('instagram_business_account')
                if ig_account:
                    print(f"   Page {i+1}: {page.get('name')}")
                    print(f"   Instagram ID: {ig_account.get('id')}")
                    print(f"   Instagram Username: {ig_account.get('username', 'N/A')}")
                    return ig_account.get('id')
                else:
                    print(f"   Page {i+1}: {page.get('name')} - No Instagram account connected")
    except Exception as e:
        print(f"   Error: {e}")

    # Approach 2: Using me/accounts without fields first, then individual page calls
    print("\n2. Trying alternative approach...")
    try:
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}"
        response = requests.get(url)
        print(f"   Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"   Found {len(pages)} total pages")

            # For each page, try to get its Instagram account separately
            for page in pages:
                page_id = page['id']
                page_name = page['name']
                print(f"   Checking page: {page_name} (ID: {page_id})")

                ig_url = f"https://graph.facebook.com/v18.0/{page_id}/instagram_business_account?access_token={FB_ACCESS_TOKEN}"
                ig_response = requests.get(ig_url)

                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    if 'id' in ig_data:
                        print(f"   SUCCESS! Instagram ID found: {ig_data['id']}")
                        print(f"   Instagram Username: {ig_data.get('username', 'N/A')}")
                        return ig_data['id']
                    else:
                        print(f"   No Instagram account linked to this page")
                else:
                    print(f"   Could not access Instagram account for this page: {ig_response.status_code}")
        else:
            print(f"   Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Approach 3: Try to get page information if we know the page ID
    print("\n3. If you know your Facebook Page ID, we can try directly...")
    print("   Try this URL in your browser to find your page ID:")
    print(f"   https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN[:20]}...&fields=id,name")

    return None

if __name__ == "__main__":
    ig_id = find_ig_account()

    if ig_id:
        print(f"\n" + "="*50)
        print(f"Instagram Business Account ID found: {ig_id}")
        print("You can now update your .env file with this ID")
        print("="*50)
    else:
        print(f"\n" + "="*50)
        print("Could not automatically find your Instagram Business Account ID")
        print("This might mean:")
        print("1. You don't have a Facebook Page connected to Instagram")
        print("2. The connection between Facebook Page and Instagram is not properly set up")
        print("3. The permissions are in place but the accounts aren't linked")
        print("="*50)