#!/usr/bin/env python3
"""
Simple Instagram API test
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

# Print current config
print("Current configuration:")
from config import FB_ACCESS_TOKEN, IG_ID
print(f"FB_ACCESS_TOKEN set: {'Yes' if FB_ACCESS_TOKEN else 'No'}")
print(f"IG_ID set: {'Yes' if IG_ID else 'No'}")
print(f"IG_ID value: {IG_ID}")

print("\nTesting Instagram API connection...")
ig = InstagramAPISkill()

# Try to get account info
print("\nTrying to get account info...")
account_info = ig.get_account_info()
print("Account info result:", account_info)

if "error" in account_info:
    print("\nThe token may not have proper permissions or the IG_ID may be incorrect.")
    print("You need to:")
    print("1. Make sure you have a Facebook Page connected to an Instagram Business Account")
    print("2. Get the correct Instagram Business Account ID")
    print("3. Ensure your token has the right permissions")
else:
    print("Account info retrieved successfully!")

    # Try a test post
    print("\nTrying to make a test post...")
    result = ig.post("Test post from AI Employee Vault! #AI #Automation", "post_image.png")
    print("Post result:", result)