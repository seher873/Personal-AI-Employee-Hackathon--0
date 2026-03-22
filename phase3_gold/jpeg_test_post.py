#!/usr/bin/env python3
"""
Test post with JPEG format image - Instagram is strict about image formats
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

def test_with_jpeg_image():
    print("INSTAGRAM API - JPEG FORMAT TEST")
    print("="*50)

    ig = InstagramAPISkill()

    print(f"Instagram ID: {ig.ig_id}")
    print(f"Account: @urojk772026")

    # Use a JPEG image which is more likely to be accepted by Instagram
    jpeg_image_url = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"

    caption = "Test from AI Employee Vault - JPEG format! Instagram Graph API working. #AI #Automation #Testing"

    print(f"\nTesting with JPEG image...")
    print(f"Caption: {caption}")

    # First, let's verify what images are accessible
    print(f"\nTrying known working image format...")

    result = ig.post(caption, jpeg_image_url)

    print(f"Post Result: {result}")

    if result.get('success'):
        print(f"\n🎉 SUCCESS! Post published to Instagram!")
        print(f"Post ID: {result.get('post_id')}")
        print(f"Check your Instagram: @urojk772026")
    else:
        print(f"\n❌ Post failed: {result.get('error')}")
        print(f"Status: {result.get('status_code', 'N/A')}")

        # Let's try debugging by checking if we can make a simple API call
        print(f"\nTrying to upload via the proper method with Imgur...")

        # Try to use the imgur uploader if available
        try:
            from imgur_uploader import upload_to_imgur
            from config import IMGUR_CLIENT_ID

            if not IMGUR_CLIENT_ID or IMGUR_CLIENT_ID == "your_imgur_client_id_here":
                print("Imgur Client ID not configured - this is the issue!")
                print("\nSOLUTION:")
                print("1. Go to: https://api.imgur.com/oauth2/addclient")
                print("2. Register new application")
                print("3. Get Client ID")
                print("4. Set IMGUR_CLIENT_ID in your .env file")
                print("5. Try again")
            else:
                # Try to upload a local image to Imgur
                if os.path.exists("post_image.png"):
                    print("Attempting to upload local image to Imgur...")
                    imgur_result = upload_to_imgur("post_image.png")
                    print(f"Imgur upload result: {imgur_result}")

                    if imgur_result.get("success"):
                        # Try posting with the Imgur URL
                        imgur_url = imgur_result["url"]
                        print(f"Trying to post with Imgur URL: {imgur_url}")
                        result2 = ig.post(caption, imgur_url)
                        print(f"Result with Imgur: {result2}")
        except ImportError:
            print("Imgur uploader not available")
        except Exception as e:
            print(f"Error with Imgur: {e}")

if __name__ == "__main__":
    test_with_jpeg_image()