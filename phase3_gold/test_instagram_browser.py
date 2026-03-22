"""
Instagram Browser Post Test
Uses browser automation (not API) - works even with expired API tokens
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Skills.skill_instagram import InstagramSkill

print("=" * 60)
print("Instagram Browser Post Test")
print("=" * 60)

# Initialize Instagram skill
ig = InstagramSkill()

# Image path
image_path = os.path.join(os.path.dirname(__file__), "pictures", "ai-employee.jpg")

if not os.path.exists(image_path):
    print(f"\n[ERROR] Image not found: {image_path}")
    print("    Please add ai-employee.jpg to pictures folder")
    sys.exit(1)

print(f"\n[OK] Image found: {image_path}")

# Caption
caption = "AI Employee is ready to work! #AI #Automation #Productivity"
print(f"[OK] Caption: {caption}".encode('cp1252', errors='replace').decode('cp1252'))

print("\n" + "=" * 60)
print("Browser will open - Login to Instagram if needed")
print("Then post will be created automatically")
print("=" * 60)

# Post
result = ig.post(caption, image_path)

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

if result.get("success"):
    print("\n    POST SUCCESSFUL!")
    print(f"    Caption: {result.get('text', '')[:50]}...")
    print(f"    Image: {result.get('image', '')}")
else:
    print("\n    POST FAILED")
    print(f"    Error: {result.get('error', 'Unknown')}")

print("\n" + "=" * 60)
print("Summary:", ig.generate_summary())
print("=" * 60)
