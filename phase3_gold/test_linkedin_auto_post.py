#!/usr/bin/env python3
"""
Quick LinkedIn Auto Post Test
Tests posting to LinkedIn using API
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")

print("=" * 60)
print("LinkedIn Auto Post Test")
print("=" * 60)
print(f"Client ID: {CLIENT_ID}")
print(f"Token Present: {'Yes' if ACCESS_TOKEN else 'NO'}")
print("=" * 60)

# Test 1: Get Profile (using v1 API which works with 'profile' scope)
print("\n[1/3] Getting your profile...")
url = "https://api.linkedin.com/v1/me?format=json"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    profile = response.json()
    name = profile.get('firstName', {}).get('localized', 'Unknown') + ' ' + profile.get('lastName', {}).get('localized', 'User')
    print(f"✓ Connected as: {name}")
    person_id = profile.get('id', '')
    person_urn = f"urn:li:member:{person_id}"
    print(f"  Member URN: {person_urn}")
else:
    print(f"✗ Error: {response.text}")
    print("\nTrying alternative endpoint...")
    # Try v2 me with different fields
    url = "https://api.linkedin.com/v2/me"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile = response.json()
        name = profile.get('localizedFirstName', 'Unknown') + ' ' + profile.get('localizedLastName', 'User')
        print(f"✓ Connected as: {name}")
        person_urn = f"urn:li:person:{profile.get('id', '')}"
        print(f"  URN: {person_urn}")
    else:
        print(f"✗ Still failed: {response.text}")
        person_urn = ""

# Test 2: Post Test Message
print("\n[2/3] Posting test message...")

if not person_urn:
    print("✗ Cannot post - profile URN not available")
    print("\nYour token needs 'profile' or 'r_liteprofile' permission to get your member ID")
    sys.exit(1)

post_text = f"""🤖 AI Employee Auto Post Test

Testing automated LinkedIn posting via API.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AI #Automation #LinkedInAPI #AutoPost"""

payload = {
    "author": person_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": post_text
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

url = "https://api.linkedin.com/v2/ugcPosts"
response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    post_id = result.get('id', 'unknown')
    print(f"✓ SUCCESS! Post created!")
    print(f"  Post ID: {post_id}")
    print(f"  URL: https://www.linkedin.com/feed/update/{post_id}")
else:
    print(f"✗ Post failed: {response.status_code}")
    print(f"  Response: {response.text}")

# Test 3: Save to Done folder
print("\n[3/3] Saving to audit log...")
done_dir = os.path.join(os.path.dirname(__file__), "Done")
os.makedirs(done_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(done_dir, f'{timestamp}_linkedin_auto_post.md')

content = f"""---
type: linkedin_auto_post
timestamp: {datetime.now().isoformat()}
status: {'published' if response.status_code == 201 else 'failed'}
---

# LinkedIn Auto Post Test

**Posted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content

{post_text}

## Result

{'✅ Published successfully via API' if response.status_code == 201 else f'❌ Failed: {response.status_code}'}

## API Response

```json
{response.text}
```
"""

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Saved to: {log_file}")

print("\n" + "=" * 60)
if response.status_code == 201:
    print("SUCCESS! Auto post test completed!")
else:
    print("FAILED! Check permissions on your LinkedIn app.")
    print("\nRequired permissions:")
    print("  - r_liteprofile (to read profile)")
    print("  - w_member_social (to post)")
    print("\nAdd permissions at:")
    print("  https://www.linkedin.com/developers/apps")
print("=" * 60)
