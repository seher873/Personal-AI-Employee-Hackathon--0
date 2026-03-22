#!/usr/bin/env python3
"""
Simple LinkedIn Token Test
Direct API call - no extra logic
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get credentials
TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")

print("=" * 60)
print("LinkedIn Token Test")
print("=" * 60)
print(f"Client ID: {CLIENT_ID}")
print(f"Token: {TOKEN[:20]}...")
print()

# Test 1: Get Profile (using v2 API)
print("[Test 1] GET /me (v2 API)")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}

response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
print()

# Test 2: Get Profile (using v1 API - alternative)
print("[Test 2] GET /me (v1 API - alternative)")
headers_v1 = {
    "Authorization": f"Bearer {TOKEN}"
}

response = requests.get("https://api.linkedin.com/v1/me?format=json", headers=headers_v1)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
print()

# Test 3: Try posting
print("[Test 3] Try to create a post")
post_data = {
    "author": f"urn:li:person:YOUR_ID",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Test post"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(
    "https://api.linkedin.com/v2/ugcPosts",
    headers=headers,
    json=post_data
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
