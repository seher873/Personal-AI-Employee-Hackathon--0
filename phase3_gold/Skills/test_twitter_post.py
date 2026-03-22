#!/usr/bin/env python3
"""
Test Twitter Post
Simple test for Twitter posting
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from skill_twitter import TwitterSkill

print("=" * 60)
print("TWITTER POST TEST")
print("=" * 60)

tw = TwitterSkill()

test_post = "AI Employee Gold Tier - Test Post from Automated System! #AI #Automation #Testing"

print(f"\nPosting: {test_post}")
print("\nOpening browser...")

result = tw.post(test_post)

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
print(f"Success: {result.get('success', False)}")
if result.get('success'):
    print("Post published successfully!")
else:
    print(f"Error: {result.get('error', 'Unknown')}")
print("=" * 60)

print(tw.generate_summary())
