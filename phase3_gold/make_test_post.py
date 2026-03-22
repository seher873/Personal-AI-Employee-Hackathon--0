#!/usr/bin/env python3
"""
Make a test post to Instagram using the working API connection
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

def make_post():
    print("Creating Instagram API Skill instance...")
    ig = InstagramAPISkill()

    print(f"Token status: {'OK' if ig.access_token else 'Missing'}")
    print(f"Instagram ID: {ig.ig_id}")

    # Verify the image exists
    test_image = "post_image.png"
    if not os.path.exists(test_image):
        print(f"ERROR: Image {test_image} not found!")
        return

    print(f"Image {test_image} found, size: {os.path.getsize(test_image)} bytes")

    # Create a test post
    caption = "Test post from AI Employee Vault! This was posted using the Instagram Graph API. #AI #Automation #Testing #Success"

    print(f"\nAttempting to post to Instagram...")
    print(f"Caption: {caption}")
    print(f"Image: {test_image}")

    result = ig.post(caption, test_image)

    print(f"\nPost Result: {result}")

    if result.get('success'):
        print(f"\n✅ SUCCESS! Post published to Instagram!")
        print(f"Post ID: {result.get('post_id')}")
        print(f"Caption: {result.get('caption', '')[:50]}...")
    else:
        print(f"\n❌ Post failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print(f"\nPosting Summary: {ig.generate_summary()}")

if __name__ == "__main__":
    make_post()