#!/usr/bin/env python3
"""
LinkedIn Direct Token Request
==============================
Get token using client credentials directly
"""

import os
import urllib.request
import urllib.parse
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip('"')
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip('"')
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8081")

print("=" * 60)
print("🔑 LinkedIn Direct Token Request")
print("=" * 60)

print(f"\n✅ Client ID: {LINKEDIN_CLIENT_ID}")
print(f"✅ Client Secret: {LINKEDIN_CLIENT_SECRET[:20]}...")
print(f"✅ Redirect URI: {LINKEDIN_REDIRECT_URI}")

# Try client credentials grant (for company access)
print("\n📝 Trying client credentials flow...")

data = {
    'grant_type': 'client_credentials',
    'client_id': LINKEDIN_CLIENT_ID,
    'client_secret': LINKEDIN_CLIENT_SECRET,
    'scope': 'w_member_social w_organization_social r_organization_social'
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

req = urllib.request.Request(
    'https://www.linkedin.com/oauth/v2/accessToken',
    data=urllib.parse.urlencode(data).encode(),
    headers=headers,
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        print(f"\n✅ Token received!")
        print(f"   Access Token: {result.get('access_token', '')}")
        print(f"   Expires In: {result.get('expires_in', 'N/A')} seconds")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"\n❌ Error {e.code}: {error_body}")
    print("\n💡 Client credentials flow doesn't work for LinkedIn personal/company posts")
    print("   You need to use authorization code flow (browser-based)")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("📝 Manual Authorization Steps:")
print("=" * 60)

print("""
1. Open this URL in your browser:
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77p2b95tmb7r06&redirect_uri=http://localhost:8081&scope=w_member_social+r_liteprofile

2. Login to LinkedIn

3. Click "Authorize" or "Allow"

4. You'll be redirected to a URL like:
   http://localhost:8081/?code=AQVxK8j3mN9pL2wR5tY7uI0oP4sD6fG8hJ1kL3zX5cV7bN9mQ2wE4rT6yU8iO0pA

5. Copy the code (everything after 'code=' and before '&')

6. Run this command:
   py -3 linkedin_token_generator.py --code YOUR_CODE_HERE
""")
