#!/usr/bin/env python3
"""
LinkedIn Auto Post - Manual URN Version
Post to LinkedIn using API with manually configured member URN
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

# =============================================================================
# CONFIGURATION - Add your LinkedIn Member URN here
# =============================================================================
# Your LinkedIn Member URN (format: urn:li:member:XXXXXXXX)
# You can find this from your LinkedIn profile URL or API response
# Example: urn:li:member:123456789
LINKEDIN_MEMBER_URN = ""  # <-- Fill this in!
# =============================================================================

print("=" * 60)
print("LinkedIn Auto Post - Manual URN")
print("=" * 60)
print(f"Client ID: {CLIENT_ID}")
print(f"Token Present: {'Yes' if ACCESS_TOKEN else 'NO'}")
print(f"Member URN: {LINKEDIN_MEMBER_URN if LINKEDIN_MEMBER_URN else 'NOT SET'}")
print("=" * 60)

if not LINKEDIN_MEMBER_URN:
    print("\n[ERROR] Please set your LINKEDIN_MEMBER_URN in the script!")
    print("\nHow to find your Member URN:")
    print("1. Go to https://www.linkedin.com/developers/apps")
    print("2. Select your app")
    print("3. Go to 'Auth' tab and test the API")
    print("4. Or use: https://api.linkedin.com/v2/me with your token")
    print("5. Your URN format: urn:li:member:YOUR_ID")
    sys.exit(1)

# Test connection and post
print("\n[1/2] Testing API connection...")
url = "https://api.linkedin.com/v2/me"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

response = requests.get(url, headers=headers)
print(f"Profile API Status: {response.status_code}")

if response.status_code == 200:
    profile = response.json()
    name = profile.get('localizedFirstName', 'Unknown') + ' ' + profile.get('localizedLastName', 'User')
    print(f"✓ Connected as: {name}")
elif response.status_code == 403:
    print("⚠ Profile access denied (this is OK if you have w_member_social scope)")
    print("  Proceeding with manual URN...")
else:
    print(f"  Response: {response.text[:200]}")

# Post test message
print("\n[2/2] Posting test message...")

post_text = f"""🤖 AI Employee Auto Post Test

Testing automated LinkedIn posting via API.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AI #Automation #LinkedInAPI #AutoPost"""

payload = {
    "author": LINKEDIN_MEMBER_URN,
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
print(f"Post API Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    post_id = result.get('id', 'unknown')
    print(f"\n✓ SUCCESS! Post created!")
    print(f"  Post ID: {post_id}")
    print(f"  URL: https://www.linkedin.com/feed/update/{post_id}")
    success = True
else:
    print(f"\n✗ Post failed: {response.status_code}")
    print(f"  Response: {response.text}")
    success = False

# Save to Done folder
print("\n[3/3] Saving to audit log...")
done_dir = os.path.join(os.path.dirname(__file__), "Done")
os.makedirs(done_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(done_dir, f'{timestamp}_linkedin_auto_post.md')

content = f"""---
type: linkedin_auto_post
timestamp: {datetime.now().isoformat()}
status: {'published' if success else 'failed'}
---

# LinkedIn Auto Post Test

**Posted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content

{post_text}

## Result

{'✅ Published successfully via API' if success else f'❌ Failed: {response.status_code}'}

## API Response

```json
{response.text}
```
"""

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Saved to: {log_file}")

print("\n" + "=" * 60)
if success:
    print("SUCCESS! Auto post test completed!")
else:
    print("FAILED! Check the error message above.")
    print("\nCommon issues:")
    print("  1. Member URN format should be: urn:li:member:XXXXXXXX")
    print("  2. Token must have w_member_social scope")
    print("  3. Token must not be expired")
print("=" * 60)
