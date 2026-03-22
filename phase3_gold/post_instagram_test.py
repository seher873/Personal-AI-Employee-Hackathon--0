"""
Instagram Post Test - ai-employee.jpg
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Skills.skill_instagram_api import InstagramAPISkill

def main():
    print("=" * 60)
    print("Instagram Post Test")
    print("=" * 60)
    
    # Initialize Instagram API
    ig = InstagramAPISkill()
    
    # Check account info first
    print("\n[1] Checking Instagram Account...")
    account_info = ig.get_account_info()
    print(f"    Account Info: {account_info}")
    
    # Image path - check both locations
    image_path = None
    
    # Check pictures folder first
    pictures_path = os.path.join(os.path.dirname(__file__), "pictures", "ai-employee.jpg")
    if os.path.exists(pictures_path):
        image_path = pictures_path
        print(f"\n[OK] Found image in pictures folder: {image_path}")
    else:
        # Fallback to post_image.png
        fallback_path = os.path.join(os.path.dirname(__file__), "post_image.png")
        if os.path.exists(fallback_path):
            image_path = fallback_path
            print(f"\n[WARN] ai-employee.jpg not found, using: {image_path}")
        else:
            print("\n[ERROR] No image found!")
            print("    Please add ai-employee.jpg to pictures folder")
            return
    
    # Post to Instagram
    caption = "AI Employee is ready to work! #AI #Automation #Productivity"
    
    print(f"\n[2] Posting to Instagram...")
    print(f"    Caption: {caption}".encode('cp1252', errors='replace').decode('cp1252'))
    print(f"    Image: {image_path}")
    
    result = ig.post(caption, image_path)
    
    print(f"\n[3] Result:")
    if result.get("success"):
        print(f"    ✅ POST SUCCESSFUL!")
        print(f"    Post ID: {result.get('post_id')}")
        print(f"    Caption: {result.get('caption')}")
    else:
        print(f"    ❌ POST FAILED")
        print(f"    Error: {result.get('error')}")
    
    # Summary
    print(f"\n[4] Summary:")
    print(ig.generate_summary())
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
