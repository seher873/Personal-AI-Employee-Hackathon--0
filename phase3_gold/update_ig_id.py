#!/usr/bin/env python3
"""
Script to help update the Instagram ID in the .env file
"""
import requests
from config import FB_ACCESS_TOKEN
import json
import os

def get_instagram_accounts():
    """
    Try to get Instagram Business Accounts connected to the user's Facebook account
    """
    print("Attempting to get Instagram accounts with your token...")

    # First, get user's pages
    pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}&fields=name,instagram_business_account"

    try:
        response = requests.get(pages_url)

        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])

            if not pages:
                print("No Facebook Pages found connected to your account.")
                print("\nTo post to Instagram using the API, you need to:")
                print("1. Create a Facebook Page (if you don't have one)")
                print("2. Connect your Instagram Business Account to the Facebook Page")
                print("3. Get the Instagram Business Account ID")
                return None

            print(f"Found {len(pages)} Facebook Page(s):")
            ig_accounts = []

            for i, page in enumerate(pages):
                page_id = page['id']
                page_name = page['name']
                print(f"\nPage {i+1}: {page_name}")
                print(f"Page ID: {page_id}")

                # Check if this page has an Instagram Business Account
                ig_account = page.get('instagram_business_account')
                if ig_account:
                    ig_id = ig_account.get('id')
                    ig_username = ig_account.get('username', 'N/A')
                    print(f"  Instagram Business Account ID: {ig_id}")
                    print(f"  Instagram Username: {ig_username}")
                    ig_accounts.append({
                        'page_name': page_name,
                        'page_id': page_id,
                        'ig_id': ig_id,
                        'ig_username': ig_username
                    })
                else:
                    print(f"  No Instagram Business Account connected")

            return ig_accounts

        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"Error getting pages: {error_msg}")
            print("This might be due to insufficient permissions in your token.")
            print("Your token needs these permissions: pages_show_list, instagram_basic")
            return None

    except Exception as e:
        print(f"Error making API call: {e}")
        return None

def update_env_file(ig_id):
    """
    Update the .env file with the correct IG_ID
    """
    # Read the current .env file
    with open('.env', 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace the IG_ID line
    import re
    updated_content = re.sub(
        r'IG_ID=.*$',
        f'IG_ID={ig_id}',
        content,
        flags=re.MULTILINE
    )

    # Write back to the .env file
    with open('.env', 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"Updated IG_ID in .env file to: {ig_id}")

def main():
    print("Instagram ID Finder")
    print("=" * 50)

    print(f"Using FB Access Token: {'Yes' if FB_ACCESS_TOKEN else 'No'}")

    if not FB_ACCESS_TOKEN or 'your_' in FB_ACCESS_TOKEN:
        print("Error: Facebook access token not properly configured")
        return

    # Try to get Instagram accounts
    ig_accounts = get_instagram_accounts()

    if not ig_accounts:
        print("\n" + "="*60)
        print("MANUAL SETUP INSTRUCTIONS:")
        print("="*60)
        print("1. Go to your Facebook Page settings")
        print("2. Connect your Instagram Business Account to the Facebook Page")
        print("3. Get your Instagram Business Account ID from:")
        print("   https://business.facebook.com/creatorstudio/")
        print("4. Or use Graph API Explorer with your token to find it")
        print("="*60)
        return

    print("\n" + "="*60)
    print("FOUND INSTAGRAM ACCOUNTS:")
    print("="*60)

    for i, account in enumerate(ig_accounts):
        print(f"{i+1}. Page: {account['page_name']}")
        print(f"   Instagram ID: {account['ig_id']}")
        print(f"   Instagram Username: {account['ig_username']}")
        print()

    if len(ig_accounts) == 1:
        # If there's only one account, update the .env file
        selected_account = ig_accounts[0]
        print(f"Updating .env file with Instagram ID: {selected_account['ig_id']}")
        update_env_file(selected_account['ig_id'])

        print("\nNow you can test the Instagram API posting!")
        print("Run: python -m Skills.skill_instagram_api")
    else:
        print("Multiple Instagram accounts found.")
        print("Choose one and manually update your .env file:")
        print("IG_ID=the_instagram_id_you_want_to_use")

if __name__ == "__main__":
    main()