#!/usr/bin/env python3
"""
Test script to get connected Instagram account using the provided Facebook token
"""
import requests
import json

def test_token():
    # Use the token from config
    from config import FB_ACCESS_TOKEN

    print("Testing your token with basic user info...")

    # Try to get basic user info with the token
    url = f"https://graph.facebook.com/v18.0/me?access_token={FB_ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_info = response.json()
            print(f"User ID: {user_info.get('id')}")
            print(f"User Name: {user_info.get('name')}")
        else:
            print(f"Could not get user info: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error getting user info: {e}")

    # Try to get pages associated with this user
    print("\nTrying to get associated pages...")
    pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}"
    try:
        response = requests.get(pages_url)
        if response.status_code == 200:
            pages_data = response.json()
            pages = pages_data.get('data', [])
            if pages:
                print(f"Found {len(pages)} page(s):")
                for i, page in enumerate(pages):
                    print(f"  {i+1}. Page ID: {page['id']}, Name: {page['name']}")
                    # For each page, try to get connected Instagram account
                    ig_url = f"https://graph.facebook.com/v18.0/{page['id']}/instagram_business_account?access_token={FB_ACCESS_TOKEN}"
                    ig_response = requests.get(ig_url)
                    if ig_response.status_code == 200:
                        ig_data = ig_response.json()
                        if 'id' in ig_data:
                            print(f"     Instagram Business Account ID: {ig_data['id']}")
                            print(f"     Username: {ig_data.get('username', 'N/A')}")
                        else:
                            print(f"     No Instagram Business Account linked to this page")
                    else:
                        print(f"     Error getting Instagram account: {ig_response.status_code} - {ig_response.text}")
            else:
                print("No pages found. You need to either:")
                print("1. Create a Facebook Page and connect your Instagram Business Account to it")
                print("2. Or use browser-based posting instead of API")
        else:
            print(f"Could not get pages: {response.status_code} - {response.text}")
            print("This might be because the token doesn't have 'pages_show_list' permission")
    except Exception as e:
        print(f"Error getting pages: {e}")

if __name__ == "__main__":
    test_token()