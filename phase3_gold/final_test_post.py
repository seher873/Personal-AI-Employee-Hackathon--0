#!/usr/bin/env python3
"""
Final test post using a publicly available image
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

def test_post_with_public_image():
    print("INSTAGRAM API - FINAL TEST POST")
    print("="*50)

    print("Creating Instagram API Skill instance...")
    ig = InstagramAPISkill()

    print(f"Token configured: {'Yes' if ig.access_token else 'No'}")
    print(f"Instagram ID configured: {ig.ig_id}")

    # Use a simple public image that's known to work with Instagram API
    # Using a direct image URL from a reliable source
    public_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Python_logo%2C_RGBA_version.svg/240px-Python_logo%2C_RGBA_version.svg.png"

    caption = "Test post from AI Employee Vault - Final Test! Successfully using Instagram Graph API. #AI #Automation #Testing #Success"

    print(f"\nAttempting post...")
    print(f"Caption: {caption}")
    print(f"Image URL: {public_image_url}")

    try:
        result = ig.post(caption, public_image_url)

        print(f"\nPOST RESULT:")
        print(f"Success: {result.get('success', False)}")

        if result.get('success'):
            print(f"✅ SUCCESS! Post published to Instagram!")
            print(f"Post ID: {result.get('post_id', 'N/A')}")
            print(f"Caption: {result.get('caption', 'N/A')[:50]}...")
            print(f"Image: {result.get('image', 'N/A')}")
        else:
            print(f"❌ Post failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Status Code: {result.get('status_code', 'N/A')}")

        print(f"\nSummary: {ig.generate_summary()}")

    except Exception as e:
        print(f"Exception during posting: {e}")
        import traceback
        traceback.print_exc()

def test_account_info():
    print(f"\n{'='*50}")
    print("ACCOUNT INFORMATION:")
    ig = InstagramAPISkill()
    account_info = ig.get_account_info()
    print(f"Account Info: {account_info}")

if __name__ == "__main__":
    test_account_info()
    test_post_with_public_image()

    print(f"\n{'='*50}")
    print("TEST COMPLETE!")
    print("If the post was successful, check your Instagram @urojk772026")
    print("If it failed, verify your connection between Facebook Page and Instagram is active")
    print("="*50)