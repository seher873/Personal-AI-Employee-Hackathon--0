#!/usr/bin/env python3
"""
Instagram Post - AI Automation Topic
Professional post about AI Automation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv(override=True)

from Skills.skill_instagram_api import InstagramAPISkill

print("=" * 60)
print("AI AUTOMATION - Instagram Post")
print("=" * 60)

# Professional caption about AI Automation
caption = """🤖 AI Automation is transforming the way we work!

✨ Automate repetitive tasks
✨ Boost productivity by 10x
✨ Focus on what really matters
✨ 24/7 working employee without breaks

💼 Perfect for:
• Social Media Posting
• Customer Support
• Data Entry
• Email Management
• And much more!

🚀 The future is here. Are you ready?

#AIAutomation #ArtificialIntelligence #Automation #Productivity #DigitalTransformation #AI #Technology #BusinessAutomation #SmartWork #FutureOfWork #AIEmployee #TechInnovation #BusinessGrowth #Efficiency #Innovation
"""

print(f"\n📝 Caption:\n{caption}")

# Beautiful tech/AI related image
image_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop"

print(f"\n🖼️ Image URL: {image_url}")

print("\n📤 Posting to Instagram...")

ig = InstagramAPISkill()
result = ig.post(caption.strip(), image_url)

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

if result.get('success'):
    print("✅ POST SUCCESSFUL!")
    print(f"   Post ID: {result.get('post_id')}")
    print(f"\n🎉 Your AI Automation post is live on Instagram!")
    print(f"   Check: https://instagram.com/urojk772026")
else:
    print("❌ POST FAILED")
    print(f"   Error: {result.get('error')}")

print("=" * 60)
