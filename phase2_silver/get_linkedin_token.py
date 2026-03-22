#!/usr/bin/env python3
"""
Quick LinkedIn Token Exchange
Usage: py -3 get_linkedin_token.py --code YOUR_CODE
"""

import os
import sys
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv

load_dotenv()

CODE = sys.argv[1] if len(sys.argv) > 1 else None

if not CODE:
    print("❌ Please provide authorization code")
    print("Usage: py -3 get_linkedin_token.py YOUR_CODE_HERE")
    sys.exit(1)

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8081").strip()

print("=" * 60)
print("🔄 Exchanging code for token")
print("=" * 60)
print(f"Client ID: {CLIENT_ID}")
print(f"Redirect URI: {REDIRECT_URI}")
print(f"Code: {CODE[:30]}...")

data = {
    'grant_type': 'authorization_code',
    'code': CODE,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
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
        access_token = result.get('access_token', '')
        expires_in = result.get('expires_in', 0)
        
        print(f"\n✅ SUCCESS!")
        print(f"Access Token: {access_token}")
        print(f"Expires In: {expires_in} seconds")
        
        # Save to .env
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith('Linkedin_Access_Token') or line.strip().startswith('LINKEDIN_ACCESS_TOKEN'):
                new_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f'\nLINKEDIN_ACCESS_TOKEN={access_token}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"\n✅ Token saved to .env file!")
        
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"\n❌ Error {e.code}: {error_body}")
except Exception as e:
    print(f"\n❌ Error: {e}")
