#!/usr/bin/env python3
"""
Test Instagram posting using local images from pictures folder
This script will test the Instagram API with local images instead of Imgur
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def test_instagram_local_images():
    """Test Instagram posting with local images"""
    print("=" * 70)
    print("Instagram API Test - Local Images (No Imgur Required)")
    print("=" * 70)

    # Check if we have the required credentials
    from config import FB_ACCESS_TOKEN, IG_ID

    print(f"FB Access Token present: {'Yes' if FB_ACCESS_TOKEN else 'No'}")
    print(f"IG ID present: {'Yes' if IG_ID and IG_ID != 'your_instagram_business_account_id_here' else 'No'}")

    if not FB_ACCESS_TOKEN:
        print("\n❌ FB_ACCESS_TOKEN not set in .env file")
        print("Please set this with a valid Facebook/Instagram access token")
        return

    if not IG_ID or IG_ID == "your_instagram_business_account_id_here":
        print(f"\n⚠️  IG_ID not set properly in .env file")
        print("For now, we'll proceed but Instagram posting will fail without a valid ID")
        print("Please follow these steps to get your IG_ID:")
        print("  1. Visit https://developers.facebook.com/tools/explorer/")
        print("  2. Get a user access token with these permissions:")
        print("     - pages_show_list")
        print("     - instagram_basic")
        print("     - instagram_content_publish")
        print("  3. Make a GET request to: /me/accounts?fields=instagram_business_account")
        print("  4. Find the 'id' of your Instagram business account")

    # Find test images in pictures folder
    pictures_dir = os.path.join(os.path.dirname(__file__), "pictures")
    print(f"\nLooking for images in: {pictures_dir}")

    if not os.path.exists(pictures_dir):
        print(f"❌ Pictures directory not found: {pictures_dir}")
        return

    image_files = []
    for filename in os.listdir(pictures_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(pictures_dir, filename)
            image_files.append(image_path)

    if not image_files:
        print(f"❌ No image files found in {pictures_dir}")
        return

    print(f"✅ Found {len(image_files)} images:")
    for img in image_files:
        file_size = os.path.getsize(img)
        print(f"   - {os.path.basename(img)} ({file_size:,} bytes)")

    # Try to initialize Instagram API skill
    try:
        from Skills.skill_instagram_api import InstagramAPISkill
        ig = InstagramAPISkill()

        print(f"\n✅ Instagram API Skill initialized")
        print(f"   Access Token present: {'Yes' if ig.access_token else 'No'}")
        print(f"   IG ID: {ig.ig_id}")

        # Try to get account info (this will tell us if credentials work)
        print(f"\nGetting account info...")
        account_info = ig.get_account_info()
        if "error" not in account_info:
            print(f"✅ Account info retrieved!")
            print(f"   Username: {account_info.get('username', 'Unknown')}")
            print(f"   Followers: {account_info.get('followers_count', 0)}")
            print(f"   Media Count: {account_info.get('media_count', 0)}")
        else:
            print(f"❌ Account info error: {account_info['error']}")
            if "Invalid OAuth" in account_info['error'] or "access token" in account_info['error'].lower():
                print("   This suggests the token is invalid or lacks required permissions")

        # Test posting with each image
        print(f"\nTesting image uploads with local files...")
        print(f"(This will attempt to upload the image directly without Imgur)")

        for i, image_path in enumerate(image_files):
            print(f"\n--- Test {i+1}/{len(image_files)} ---")
            print(f"Image: {os.path.basename(image_path)}")

            # Create a test caption
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            caption = f"AI Employee Test Post #{i+1} - Direct Upload - {timestamp} #AI #Automation #Test"

            print(f"Caption: {caption}")
            print("Attempting direct upload...")

            result = ig.post(caption, image_path)

            if result.get("success"):
                print(f"✅ SUCCESS! Post ID: {result.get('post_id', 'N/A')}")
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                if result.get('status_code'):
                    print(f"   Status code: {result.get('status_code')}")

            # Wait a bit between posts
            if i < len(image_files) - 1:
                print("Waiting 5 seconds before next post...")
                import time
                time.sleep(5)

        print(f"\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        summary = ig.generate_summary()
        print(f"Total posts attempted: {summary['total_posts']}")
        print(f"Error count: {summary['error_count']}")

        if summary['recent_errors']:
            print("Recent errors:")
            for error in summary['recent_errors']:
                print(f"  - {error}")

    except ImportError as e:
        print(f"❌ Could not import InstagramAPISkill: {e}")
        print("Make sure all dependencies are installed and the file exists")
    except Exception as e:
        print(f"❌ Error during Instagram test: {e}")
        import traceback
        traceback.print_exc()

def check_requirements():
    """Check if required modules and images are available"""
    print("Checking requirements...")

    # Check for required modules
    try:
        import requests
        print("[OK] Requests module available")
    except ImportError:
        print("[ERROR] Requests module not available")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv module available")
    except ImportError:
        print("❌ python-dotenv module not available")
        return False

    return True

if __name__ == "__main__":
    print("Testing Instagram posting with local images (no Imgur)...")

    if not check_requirements():
        sys.exit(1)

    test_instagram_local_images()