#!/usr/bin/env python3
"""
Get LinkedIn Member URN
Fetches your LinkedIn member ID using the API
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

print("=" * 60)
print("LinkedIn Member URN Finder")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}

# Try different API endpoints to get member ID
endpoints = [
    ("v2/me", {"fields": "id,firstName,lastName"}),
    ("v1/me", {"format": "json"}),
    ("v2/me?", ""),  # Query string style
]

for endpoint, params in endpoints:
    print(f"\nTrying: https://api.linkedin.com/{endpoint}")
    try:
        url = f"https://api.linkedin.com/{endpoint}"
        response = requests.get(url, headers=headers, params=params if params else {})
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Response: {data}")
            
            # Extract ID
            member_id = data.get('id')
            if member_id:
                print(f"\n✓ Found Member ID: {member_id}")
                print(f"✓ Your Member URN: urn:li:member:{member_id}")
                print(f"\nAdd this to linkedin_auto_post.py:")
                print(f'  LINKEDIN_MEMBER_URN = "urn:li:member:{member_id}"')
                sys.exit(0)
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\n" + "=" * 60)
print("Could not fetch member ID automatically.")
print("\nAlternative: Get your member ID from LinkedIn profile URL")
print("1. Go to your LinkedIn profile")
print("2. Look at the URL or profile settings")
print("3. Or use LinkedIn Developer Portal to test API")
print("=" * 60)
