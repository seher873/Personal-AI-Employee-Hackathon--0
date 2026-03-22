#!/usr/bin/env python3
"""
Script to find Instagram Business Account ID using the provided access token
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_instagram_account_id(access_token):
    """
    Find Instagram Business Account ID using Facebook Page access token
    """
    print("Attempting to find Instagram Business Account ID...")

    # First, get the pages associated with the access token
    pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
    params = {
        "access_token": access_token,
        "fields": "id,name,instagram_business_account"
    }

    try:
        response = requests.get(pages_url, params=params)
        print(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")

            # If we get an error, try a simpler endpoint first to verify token validity
            me_url = f"https://graph.facebook.com/v18.0/me"
            me_params = {"access_token": access_token}
            me_response = requests.get(me_url, params=me_params)
            print(f"Me endpoint status: {me_response.status_code}")
            if me_response.status_code == 200:
                print("Token is valid for basic access")
                me_data = me_response.json()
                print(f"User: {me_data.get('name', 'Unknown')}")
            else:
                print(f"Token seems invalid: {me_response.text}")
                return None

        response.raise_for_status()
        data = response.json()

        print("Pages associated with the token:")

        if "data" in data:
            for page in data["data"]:
                page_id = page["id"]
                page_name = page.get("name", "Unknown")
                print(f"  Page ID: {page_id}, Name: {page_name}")

                # Check if this page has an Instagram Business Account linked
                if "instagram_business_account" in page:
                    ig_account = page["instagram_business_account"]
                    ig_id = ig_account["id"]
                    print(f"    Found Instagram Business Account ID: {ig_id}")
                    return ig_id
                else:
                    print(f"    No Instagram Business Account linked to this page")
        else:
            print("No pages found with this access token")

            # Alternative: Try getting page tokens first, then check for Instagram
            pages_url_simple = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
            simple_response = requests.get(pages_url_simple)
            simple_data = simple_response.json()

            print("\nTrying alternative method...")
            if "data" in simple_data:
                for page in simple_data["data"]:
                    page_id = page["id"]
                    page_access_token = page["access_token"]
                    print(f"Checking Page ID: {page_id}")

                    # Get Instagram account for this specific page
                    ig_url = f"https://graph.facebook.com/v18.0/{page_id}/instagram_business_account"
                    ig_params = {"access_token": page_access_token}
                    ig_response = requests.get(ig_url, params=ig_params)

                    if ig_response.status_code == 200:
                        ig_data = ig_response.json()
                        if "id" in ig_data:
                            ig_id = ig_data["id"]
                            print(f"  Found Instagram Business Account ID: {ig_id}")
                            print(f"  Page Access Token: {page_access_token}")

                            # Update the .env file with the found Instagram ID
                            update_env_file(ig_id)
                            return ig_id
                        else:
                            print(f"  No Instagram Business Account linked to this page")
                    else:
                        print(f"  Error checking Instagram account for page {page_id}: {ig_response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

    return None

def update_env_file(ig_id):
    """
    Update the .env file with the found Instagram ID
    """
    env_path = "phase3_gold/.env"

    # Read the current .env file
    with open(env_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find and update the IG_ID line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("IG_ID="):
            lines[i] = f"IG_ID={ig_id}\n"
            updated = True
            break

    if updated:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print(f"Updated IG_ID in .env file to: {ig_id}")
    else:
        print("Could not find IG_ID line in .env file to update")

def main():
    # Get the access token from environment
    access_token = os.getenv("FB_ACCESS_TOKEN")

    if not access_token:
        print("FB_ACCESS_TOKEN not found in .env file")
        return

    print(f"Using access token (first 20 chars): {access_token[:20]}...")
    print()

    ig_id = find_instagram_account_id(access_token)

    if ig_id:
        print(f"\nSuccessfully found Instagram Business Account ID: {ig_id}")
        print("\nYou can now use this ID for Instagram API calls!")
        print(f"Make sure IG_ID={ig_id} is set in your .env file")
    else:
        print("\nCould not find Instagram Business Account ID")
        print("\nTroubleshooting:")
        print("1. Make sure your Facebook token has the correct permissions")
        print("2. Ensure you have an Instagram Business Account linked to your Facebook Page")
        print("3. Check that your Instagram account is properly connected to a Facebook Page")

if __name__ == "__main__":
    main()