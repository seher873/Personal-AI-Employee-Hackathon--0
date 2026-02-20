#!/usr/bin/env python3
"""
LinkedIn Scheduler - Automatically posts to LinkedIn at optimal times.
Best posting times: Tue/Wed/Thu 9AM, Tue/Thu 12PM, Fri 5PM
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import schedule # type: ignore
from dotenv import load_dotenv # type: ignore
from playwright.sync_api import sync_playwright # type: ignore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
USER_DATA_DIR = "./linkedin_session"
SESSION_FILE = os.path.join(USER_DATA_DIR, "storage_state.json")
VAULT_PATH = "./Inbox"

# Ensure directories exist
Path(VAULT_PATH).mkdir(parents=True, exist_ok=True)
Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)

# Sample posts pool
SAMPLE_POSTS = [
    "🚀 Excited to share my latest project! Building automation tools that save time and boost productivity. #Automation #Tech #Innovation",
    "💡 Tip of the day: Automate repetitive tasks to focus on what really matters. What's your favorite productivity hack? #ProductivityTips #WorkSmart",
    "🎯 Goal setting isn't just about the destination - it's about the systems you build along the way. #Goals #Success #Mindset",
    "📚 Learning never stops! Just completed a new course on AI automation. The future is here. #ContinuousLearning #AI #Tech",
    "🤝 Collaboration is key to innovation. Great things happen when talented people work together. #Teamwork #Collaboration #Growth",
    "⚡ Quick reminder: Your network is your networth. Invest time in building genuine connections. #Networking #ProfessionalGrowth",
    "🔥 Friday motivation: The only impossible journey is the one you never begin. Start today! #Motivation #FridayVibes #Success",
    "📊 Data-driven decisions lead to better outcomes. Always measure, always improve. #DataDriven #Analytics #Business",
    "🌟 Small improvements every day lead to massive results over time. Keep going! #GrowthMindset #Improvement #Success",
    "💼 Professional tip: Document your processes. Future you will thank present you. #Documentation #Productivity #WorkTips",
]


def human_delay(min_ms=50, max_ms=200):
    """Human-like delay"""
    time.sleep(random.randint(min_ms, max_ms) / 1000)


import random


def get_post_content():
    """Get a random post from the sample pool or from a file"""
    # Check for custom post file
    post_file = os.path.join(VAULT_PATH, "scheduled_post.txt")
    if os.path.exists(post_file):
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        # Remove the file after reading
        os.remove(post_file)
        return content

    # Random post from pool
    return random.choice(SAMPLE_POSTS)


async def run_poster():
    """Post content to LinkedIn"""
    content = get_post_content()
    logger.info(f"📝 Posting: {content[:50]}...")

    if not os.path.exists(SESSION_FILE):
        logger.error("❌ No session found. Run: python setup_sessions.py")
        return False

    try:
        with sync_playwright() as p:
            storage = SESSION_FILE if os.path.exists(SESSION_FILE) else None

            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            context = browser.new_context(storage_state=storage)
            page = context.new_page()

            # Navigate to feed
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            human_delay(1000, 2000)

            # Click "Start a post"
            try:
                page.click('button[aria-label="Start a post"]')
                human_delay(1000, 2000)
            except Exception as e:
                logger.warning(f"Post button warning: {e}")

            # Enter content
            try:
                text_field = page.locator('div[contenteditable="true"]').first
                text_field.click()
                human_delay(300, 500)
                page.keyboard.press('Control+A')
                human_delay(200, 400)
                page.keyboard.press('Delete')
                human_delay(300, 500)
                text_field.type(content, delay=50)
                human_delay(500, 1000)
            except Exception as e:
                logger.warning(f"Text entry warning: {e}")

            # Click Post
            human_delay(1000, 2000)
            try:
                page.click('button:has-text("Post")')
                human_delay(2000, 3000)
            except Exception as e:
                logger.warning(f"Post click warning: {e}")

            # Save session
            context.storage_state(path=SESSION_FILE)
            browser.close()

            # Log to vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(VAULT_PATH, f"linkedin_post_{timestamp}.md")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# LinkedIn Post Published\n\n")
                f.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Content:**\n{content}\n\n")
                f.write(f"*Posted by LinkedIn Scheduler*\n")

            logger.info("✅ Post published successfully!")
            return True

    except Exception as e:
        logger.error(f"❌ Post failed: {e}")
        return False


def scheduled_job():
    """Job to run at scheduled times"""
    logger.info("⏰ Scheduled post time!")
    try:
        asyncio.run(run_poster())
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def setup_schedule():
    """Setup the posting schedule"""
    # Best LinkedIn posting times
    schedule.every().tuesday.at("09:00").do(scheduled_job)
    schedule.every().wednesday.at("09:00").do(scheduled_job)
    schedule.every().thursday.at("09:00").do(scheduled_job)
    schedule.every().tuesday.at("12:00").do(scheduled_job)
    schedule.every().thursday.at("12:00").do(scheduled_job)
    schedule.every().friday.at("17:00").do(scheduled_job)

    logger.info("📅 Schedule: Tue/Wed/Thu 9AM | Tue/Thu 12PM | Fri 5PM")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("🧪 Running test post...")
        asyncio.run(run_poster())
    else:
        setup_schedule()
        print("\n🕐 LinkedIn Scheduler running...")
        print("📅 Posts scheduled for optimal times")
        print("⏹️  Press Ctrl+C to stop\n")

        while True:
            schedule.run_pending()
            nxt = schedule.next_run()
            if nxt:
                diff = nxt - datetime.now()
                h = int(diff.total_seconds() // 3600)
                m = int((diff.total_seconds() % 3600) // 60)
                print(f"\r⏰ Next post in: {h}h {m}m   ", end="", flush=True)
            time.sleep(60)


if __name__ == "__main__":
    main()
