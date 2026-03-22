#!/usr/bin/env python3
"""
Test Instagram Post
Simple test for Instagram posting
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from skill_instagram import InstagramSkill

print("=" * 60)
print("INSTAGRAM POST TEST")
print("=" * 60)

ig = InstagramSkill()

test_post = "AI Employee Gold Tier - Test Post! #AI #Automation #Testing"

print(f"\nPosting: {test_post}")
print("\nOpening browser...")

# Instagram requires image, use placeholder if exists
import os
test_image = 'post_image.png' if os.path.exists('post_image.png') else None

if test_image:
    print(f"Using image: {test_image}")
    result = ig.post(test_post, test_image)
else:
    print("No image available - Instagram requires images")
    print("Skipping post test, just testing login...")
    result = {"success": False, "error": "No image available for Instagram"}

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
print(f"Success: {result.get('success', False)}")
if result.get('success'):
    print("Post published successfully!")
else:
    print(f"Error: {result.get('error', 'Unknown')}")
print("=" * 60)

print(ig.generate_summary())
