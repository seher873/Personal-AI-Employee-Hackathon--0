#!/usr/bin/env python3
"""
Test LinkedIn API Connection
============================
Quick test to verify LinkedIn API credentials work
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from Skills.skill_linkedin_api import LinkedInAPIClient


def main():
    print("=" * 60)
    print("LinkedIn API - Connection Test")
    print("=" * 60)

    try:
        # Initialize client
        client = LinkedInAPIClient()
        print("\n[OK] API Client initialized")

        # Test 1: Get profile
        print("\n[Test 1] Fetching user profile...")
        profile = client.get_user_profile()
        if profile:
            name = profile.get('localizedFirstName', 'Unknown') + ' ' + profile.get('localizedLastName', 'User')
            print(f"  [OK] Connected as: {name}")
            print(f"  [OK] Profile ID: {profile.get('id', 'N/A')}")
        else:
            print("  [ERROR] Failed to fetch profile")

        # Test 2: Get company page
        print("\n[Test 2] Fetching company page...")
        company = client.get_company_page()
        if company:
            print(f"  [OK] Company: {company.get('localizedName', 'Unknown')}")
            print(f"  [OK] Company ID: {company.get('id', 'N/A')}")
        else:
            print("  [WARN] Failed to fetch company (COMPANY_URN may not be set)")

        # Test 3: Post test message (commented out by default)
        print("\n[Test 3] Post test (DISABLED by default)")
        print("  To enable, uncomment the code in test_linkedin_api.py")
        # Uncomment below to actually post:
        # result = client.post_text(
        #     text="Testing LinkedIn API from AI Employee! #Automation",
        #     company=False
        # )
        # if result.get('success'):
        #     print(f"  [OK] Post successful! ID: {result['post_id']}")
        # else:
        #     print(f"  [ERROR] Post failed: {result.get('error')}")

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check .env file has LINKEDIN_CLIENT_ID")
        print("2. Check .env file has LINKEDIN_ACCESS_TOKEN")
        print("3. Verify token is not expired")
        print("4. Run: python config.py to check all credentials")


if __name__ == '__main__':
    main()
