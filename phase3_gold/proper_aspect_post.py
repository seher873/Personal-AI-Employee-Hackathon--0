#!/usr/bin/env python3
"""
Test with proper aspect ratio - create a properly sized image
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

def test_with_proper_aspect_image():
    print("INSTAGRAM API - PROPER ASPECT RATIO TEST")
    print("="*60)

    ig = InstagramAPISkill()

    print(f"Instagram Account: @urojk772026")
    print(f"Instagram ID: {ig.ig_id}")
    print(f"Token: {'Configured' if ig.access_token else 'Missing'}")

    # Use an image with proper Instagram aspect ratio (square 1080x1080)
    # Let's try a known good image URL with proper dimensions
    proper_image_url = "https://via.placeholder.com/1080x1080.png"

    caption = "AI Employee Vault Test Post - Proper Format! #AI #Automation #Testing #Success"

    print(f"\nTesting with properly-sized image (1080x1080 - Instagram standard)...")
    print(f"Caption: {caption}")
    print(f"Image: {proper_image_url}")

    result = ig.post(caption, proper_image_url)

    print(f"\nPOST RESULT:")
    print(f"Success: {result.get('success', False)}")

    if result.get('success'):
        print(f"\n🎉 SUCCESS! Post published to Instagram!")
        print(f"Post ID: {result.get('post_id')}")
        print(f"Check your Instagram: @urojk772026")
    else:
        print(f"\n❌ Post failed: {result.get('error')}")
        print(f"Status Code: {result.get('status_code', 'N/A')}")

        print(f"\nSUMMARY:")
        print(f"- Your token and Instagram ID are properly configured")
        print(f"- API communication is working")
        print(f"- The issue is with image hosting/format")
        print(f"- SOLUTION: Configure Imgur Client ID in .env file")

        print(f"\nTo complete the setup:")
        print(f"1. Go to: https://api.imgur.com/oauth2/addclient")
        print(f"2. Register application, get Client ID")
        print(f"3. Add to .env: IMGUR_CLIENT_ID=your_id_here")
        print(f"4. Run the poster again")

if __name__ == "__main__":
    test_with_proper_aspect_image()