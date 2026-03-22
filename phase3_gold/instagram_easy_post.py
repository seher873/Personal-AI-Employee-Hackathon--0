#!/usr/bin/env python3
"""
Instagram Poster - Easy Version
Bas image URL paste karo aur post karo!
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv(override=True)

from Skills.skill_instagram_api import InstagramAPISkill

print("=" * 60)
print("INSTAGRAM POSTER - EASY MODE")
print("=" * 60)

# Step 1: Image URL lo
print("\n📋 STEP 1: Image URL enter karo")
print("-" * 60)
print("Imgur se URL kaise lein:")
print("1. https://imgur.com/upload pe jao")
print("2. Apni image upload karo")
print("3. Image par right-click karke 'Copy image address' karo")
print("4. Yahan paste karo\n")

image_url = input("Image URL: ").strip()

if not image_url:
    print("❌ URL empty hai!")
    exit(1)

if not image_url.startswith('http'):
    print("❌ URL valid nahi hai! http:// ya https:// se start hona chahiye")
    exit(1)

print(f"✅ URL: {image_url}")

# Step 2: Caption lo
print("\n📋 STEP 2: Caption enter karo")
print("-" * 60)

caption = input("Caption: ").strip()

if not caption:
    caption = "Posted via AI Employee! #AI #Automation"
    print(f"   Default caption use kar rahe hain: {caption}")

print(f"✅ Caption: {caption}")

# Step 3: Instagram post
print("\n📤 STEP 3: Posting to Instagram...")
print("-" * 60)

ig = InstagramAPISkill()
result = ig.post(caption, image_url)

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

if result.get('success'):
    print("✅ POST SUCCESSFUL!")
    print(f"   Post ID: {result.get('post_id')}")
    print(f"   Caption: {caption}")
    print(f"   Image: {image_url}")
    print("\n🎉 Aapka Instagram post publish ho gaya!")
    print(f"   View: https://instagram.com/p/{result.get('post_id')}")
else:
    print("❌ POST FAILED")
    print(f"   Error: {result.get('error')}")

print("=" * 60)
