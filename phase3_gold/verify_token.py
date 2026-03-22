#!/usr/bin/env python3
"""
Verify token functionality with basic calls
"""
import requests
from config import FB_ACCESS_TOKEN

def verify_token():
    print("TOKEN VERIFICATION")
    print("=" * 40)

    # Test 1: Basic user info
    print("\n1. Testing basic user info access...")
    try:
        url = f"https://graph.facebook.com/v18.0/me?access_token={FB_ACCESS_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"   OK User ID: {data['id']}")
            print(f"   OK Name: {data['name']}")
        else:
            print(f"   FAIL: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   FAIL: {e}")

    # Test 2: Debug token info
    print("\n2. Testing token debug info...")
    try:
        url = f"https://graph.facebook.com/v18.0/debug_token?input_token={FB_ACCESS_TOKEN}&access_token={FB_ACCESS_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"   OK Token valid: {data['data']['is_valid']}")
            print(f"   OK Expires at: {data['data'].get('expires_at', 'Never')}")
            print(f"   OK Permissions: {data['data']['scopes']}")
        else:
            print(f"   FAIL: {response.status_code}")
    except Exception as e:
        print(f"   FAIL: {e}")

    # Test 3: Try getting pages (maybe with a different permission)
    print("\n3. Testing if we can access pages...")
    try:
        # Try a more basic pages call
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}&fields=name"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"   OK Found {len(pages)} pages")
            for page in pages:
                print(f"     - {page['name']} (ID: {page['id']})")
        else:
            print(f"   FAIL: {response.status_code} - {response.text}")
            print(f"   This confirms the 'accounts' field is not accessible, even though token has pages_show_list permission")
    except Exception as e:
        print(f"   FAIL: {e}")

    # Test 4: Check if this is a personal access token issue
    print("\n4. Checking if this is a personal vs page token issue...")
    print(f"   Your token seems valid but might be a user token without proper page connections")
    print(f"   You need to have:")
    print(f"   - A Facebook Page created or claimed")
    print(f"   - Instagram Business Account connected to that page")
    print(f"   - Proper tokens with the right permissions")

if __name__ == "__main__":
    verify_token()