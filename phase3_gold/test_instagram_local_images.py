#!/usr/bin/env python3
"""
Test Instagram posting using local images from pictures folder
instead of using Imgur for URL hosting.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from Skills.skill_instagram_api import InstagramAPISkill

def test_instagram_local_posting():
    """Test Instagram posting with local images"""
    print("=" * 70)
    print("Instagram API Test - Local Images")
    print("=" * 70)

    # Initialize Instagram API skill
    print("\nInitializing Instagram API skill...")
    ig = InstagramAPISkill()

    # Check account info
    print("\nChecking account info...")
    account_info = ig.get_account_info()
    if "error" not in account_info:
        print(f"✅ Account: {account_info.get('username', 'Unknown')}")
        print(f"   Followers: {account_info.get('followers_count', 0)}")
        print(f"   Media Count: {account_info.get('media_count', 0)}")
    else:
        print(f"❌ Account info error: {account_info['error']}")
        print("⚠️  Make sure IG_ID and FB_ACCESS_TOKEN are properly configured in .env")

    # Find test images in pictures folder
    pictures_dir = os.path.join(os.path.dirname(__file__), "pictures")
    print(f"\nLooking for images in: {pictures_dir}")

    if not os.path.exists(pictures_dir):
        print(f"❌ Pictures directory not found: {pictures_dir}")
        return

    image_files = []
    for filename in os.listdir(pictures_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            image_path = os.path.join(pictures_dir, filename)
            image_files.append(image_path)

    if not image_files:
        print(f"❌ No image files found in {pictures_dir}")
        return

    print(f"✅ Found {len(image_files)} images:")
    for img in image_files:
        file_size = os.path.getsize(img)
        print(f"   - {os.path.basename(img)} ({file_size:,} bytes)")

    # Test posting with each image
    print(f"\nTesting Instagram posts with local images...")

    for i, image_path in enumerate(image_files):
        print(f"\n--- Test {i+1}/{len(image_files)} ---")
        print(f"Image: {os.path.basename(image_path)}")

        # Create a unique caption for each test
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption = f"AI Employee Test Post #{i+1} - {timestamp} #AI #Automation #Testing"

        print(f"Caption: {caption}")
        print("Uploading and posting...")

        # Post to Instagram using local image
        result = ig.post(caption, image_path)

        if result.get("success"):
            print(f"✅ SUCCESS! Post ID: {result.get('post_id', 'N/A')}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            print(f"   Status code: {result.get('status_code', 'N/A')}")

        # Wait a bit between posts
        if i < len(image_files) - 1:
            print("Waiting 10 seconds before next post...")
            import time
            time.sleep(10)

    # Print final summary
    print(f"\n" + "=" * 70)
    print("Final Summary")
    print("=" * 70)
    summary = ig.generate_summary()
    print(f"Total posts attempted: {summary['total_posts']}")
    print(f"Error count: {summary['error_count']}")

    if summary['recent_errors']:
        print("Recent errors:")
        for error in summary['recent_errors']:
            print(f"  - {error}")

def check_credentials():
    """Check if required Instagram credentials are set"""
    print("Checking credentials...")

    # Import config to check credentials
    from config import FB_ACCESS_TOKEN, IG_ID

    issues = []
    if not FB_ACCESS_TOKEN or FB_ACCESS_TOKEN == "your_facebook_access_token_here":
        issues.append("FB_ACCESS_TOKEN not set in .env")
    if not IG_ID or IG_ID == "your_instagram_business_account_id_here":
        issues.append("IG_ID not set in .env")

    if issues:
        print("❌ Missing credentials:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease update your .env file with proper credentials")
        return False
    else:
        print("✅ All required credentials are set")
        return True

if __name__ == "__main__":
    print("Testing Instagram posting with local images...")

    if not check_credentials():
        sys.exit(1)

    test_instagram_local_posting()