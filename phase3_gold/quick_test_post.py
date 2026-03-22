"""
Quick Test Post - API-based
Gold Tier - Test posting to Facebook, Instagram, WhatsApp
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from social_post_watcher import SocialPostWatcher


def main():
    print("\n" + "=" * 60)
    print("Quick Test Post - API-based Social Media Posting")
    print("=" * 60)

    watcher = SocialPostWatcher()

    # Test message
    test_text = "Test post from AI Employee! [robot] #AI #Automation #Phase3Gold"

    # Check if test image exists
    test_image = os.path.join(os.path.dirname(__file__), "post_image.png")

    if not os.path.exists(test_image):
        print(f"\n[WARN] Test image not found: {test_image}")
        print("Creating a simple test image...")

        # Create a simple test image
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new('RGB', (512, 512), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((256, 256), "Test Post", fill=(255, 255, 255), anchor="mm")
            img.save(test_image)
            print(f"[OK] Created test image: {test_image}")

        except ImportError:
            print("[WARN] PIL not available. Posting text only.")
            test_image = None
        except Exception as e:
            print(f"[WARN] Could not create image: {e}")
            test_image = None
    else:
        print(f"[OK] Using existing image: {test_image}")

    # Post to all platforms
    print("\n[POST] Posting to all platforms...")
    print(f"Text: {test_text}")
    print(f"Image: {test_image if test_image else 'None'}")

    results = watcher.post_to_all(
        text=test_text,
        image_path=test_image,
        whatsapp_recipients=[]  # Add numbers here if testing WhatsApp
    )

    # Print results
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)

    if results["facebook"]:
        status = "[OK]" if results["facebook"].get("success") else "[FAIL]"
        print(f"{status} Facebook: {results['facebook'].get('post_id', results['facebook'].get('error', 'Unknown'))}")

    if results["instagram"]:
        status = "[OK]" if results["instagram"].get("success") else "[FAIL]"
        print(f"{status} Instagram: {results['instagram'].get('post_id', results['instagram'].get('error', 'Unknown'))}")

    if results["whatsapp"]:
        for i, wa_result in enumerate(results["whatsapp"], 1):
            status = "[OK]" if wa_result.get("success") else "[FAIL]"
            print(f"{status} WhatsApp #{i}: {wa_result.get('message_id', wa_result.get('error', 'Unknown'))}")

    # Print stats
    watcher.print_stats()

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
