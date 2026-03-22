"""
Hackathon Demo - Complete Social Media Automation
Post to Facebook and Instagram with single command

Usage:
    py hackathon_demo.py "Your message here"
    py hackathon_demo.py "Message" "path/to/image.png"
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_post_watcher import SocialPostWatcher


def main():
    # Handle Windows console encoding
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "=" * 60)
    print("AI Employee - Hackathon Social Media Automation")
    print("=" * 60)
    
    # Get message from command line or use default
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = f"Hello from AI Employee! 🤖 Posted at {datetime.now().strftime('%H:%M')} #AI #Automation #Hackathon"
    
    # Get image from command line or use default
    if len(sys.argv) > 2:
        image_path = sys.argv[2]
    else:
        # Create a test image if doesn't exist
        image_path = "hackathon_post.png"
        if not os.path.exists(image_path):
            print(f"\n[INFO] Creating test image: {image_path}")
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (1080, 1080), color=(25, 25, 112))
                d = ImageDraw.Draw(img)
                d.text((540, 540), "AI Employee\nHackathon Demo", 
                       fill=(255, 255, 255), anchor="mm", font_size=48)
                img.save(image_path)
                print(f"[OK] Image created")
            except Exception as e:
                print(f"[WARN] Could not create image: {e}")
                image_path = None
    
    print(f"\n[MESSAGE] {message}")
    print(f"[IMAGE] {image_path if image_path else 'None'}")
    
    # Initialize watcher
    watcher = SocialPostWatcher()
    
    # Post to Facebook
    print("\n" + "-" * 60)
    print("📘 Posting to Facebook...")
    print("-" * 60)
    fb_result = watcher.post_to_facebook(message, image_path)
    
    if fb_result.get("success"):
        print(f"[OK] Facebook post successful!")
        print(f"    Post ID: {fb_result.get('post_id')}")
        print(f"    URL: https://facebook.com/{fb_result.get('post_id')}")
    else:
        print(f"[FAIL] Facebook post failed: {fb_result.get('error')}")
    
    # Post to Instagram
    print("\n" + "-" * 60)
    print("📸 Posting to Instagram...")
    print("-" * 60)
    
    if image_path:
        ig_result = watcher.post_to_instagram(message, image_path)
        
        if ig_result.get("success"):
            print(f"[OK] Instagram post successful!")
            print(f"    Post ID: {ig_result.get('post_id', 'Processing')}")
        else:
            print(f"[FAIL] Instagram post failed: {ig_result.get('error')}")
    else:
        print("[SKIP] Instagram requires an image")
    
    # Print stats
    print("\n" + "=" * 60)
    print("📊 Results Summary")
    print("=" * 60)
    watcher.print_stats()
    
    print("\n" + "=" * 60)
    print("✅ Hackathon Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
