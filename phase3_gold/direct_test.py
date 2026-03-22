#!/usr/bin/env python3
"""
Direct test using your access token with common IG account patterns
"""

import requests
from config import FB_ACCESS_TOKEN, IG_USERNAME
import json
import os

# This might work if we can derive the IG ID from the username
def test_direct_post():
    print("Testing direct posting with your token...")

    print(f"FB Access Token: {'Present (first 10 chars)' if FB_ACCESS_TOKEN else 'Missing'}")

    # Try to get user ID from the token itself
    try:
        user_url = f"https://graph.facebook.com/v18.0/me?access_token={FB_ACCESS_TOKEN}"
        user_response = requests.get(user_url)
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"User ID: {user_data.get('id')}")
            print(f"User Name: {user_data.get('name', 'N/A')}")
        else:
            print(f"Could not get user info: {user_response.status_code}")
    except Exception as e:
        print(f"Error getting user info: {e}")

    # Try to use the token directly with your Instagram username
    # This is a test to see if we can create a media object
    print(f"\nTrying to create a media object with your token...")
    print(f"This will test if your token has the right permissions for Instagram posting")

    # We'll need to have the IG_ID to proceed, but let's at least verify the token works
    print(f"\nTOKEN VERIFICATION:")
    print(f"Token starts with: {FB_ACCESS_TOKEN[:10]}...")
    print(f"Token length: {len(FB_ACCESS_TOKEN)} characters")

    # Test basic permissions
    test_url = f"https://graph.facebook.com/v18.0/debug_token?input_token={FB_ACCESS_TOKEN}&access_token={FB_ACCESS_TOKEN}"
    try:
        debug_response = requests.get(test_url)
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"Token is valid: {debug_data.get('data', {}).get('is_valid', False)}")
            scopes = debug_data.get('data', {}).get('scopes', [])
            print(f"Token permissions: {scopes}")

            # Check for required scopes
            required_scopes = ['instagram_basic', 'instagram_content_publish', 'pages_show_list']
            missing_scopes = [scope for scope in required_scopes if scope not in scopes]

            if missing_scopes:
                print(f"Missing required permissions: {missing_scopes}")
                print("This explains why API-based posting isn't working.")
            else:
                print("All required permissions appear to be present!")

        else:
            print("Could not debug token, but it might still be valid for basic operations")
    except Exception as e:
        print(f"Could not debug token: {e}")

    print(f"\nTo successfully post to Instagram via API, you need:")
    print(f"1. A Facebook Page connected to an Instagram Business Account")
    print(f"2. The Instagram Business Account ID (IG_ID)")
    print(f"3. A token with proper permissions (your token seems to have the right format)")
    print(f"\nCurrent IG_ID in config: {os.environ.get('IG_ID', 'Not set properly in environment')}")

    # Note: Without the IG_ID, we can't actually post, but we can at least confirm the token format is valid

if __name__ == "__main__":
    test_direct_post()