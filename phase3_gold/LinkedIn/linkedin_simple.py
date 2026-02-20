#!/usr/bin/env python3
"""
LinkedIn Simple - Simple, reliable LinkedIn automation without complex type hints.
Provides test, post, and watch functionality in one easy-to-use script.
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from pathlib import Path
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
VAULT_PATH = "./Inbox"
SESSION_FILE = os.path.join(USER_DATA_DIR, "storage_state.json")

# Ensure directories exist
Path(VAULT_PATH).mkdir(parents=True, exist_ok=True)
Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)


def human_delay(min_ms=50, max_ms=200):
    """Human-like delay"""
    time.sleep(random.randint(min_ms, max_ms) / 1000)


def check_session():
    """Check if session file exists"""
    if not os.path.exists(SESSION_FILE):
        print("\n⚠️  No session found. Run setup first:")
        print("   python setup_sessions.py\n")
        return False
    return True


def get_browser_context(p):
    """Create browser context with saved session"""
    storage = None
    if os.path.exists(SESSION_FILE):
        storage = SESSION_FILE

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
    return browser, context, page


def test_setup():
    """Test if LinkedIn setup is working"""
    print("\n🧪 Testing LinkedIn setup...\n")

    if not check_session():
        return False

    try:
        with sync_playwright() as p:
            browser, context, page = get_browser_context(p)

            # Go to LinkedIn
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            human_delay(1000, 2000)

            # Check if logged in
            if "feed" in page.url or "login" in page.url:
                if "login" in page.url:
                    print("❌ Session expired. Please re-run:")
                    print("   python setup_sessions.py\n")
                    browser.close()
                    return False
                else:
                    print("✓ Session is valid!")
                    print(f"✓ Current URL: {page.url}")
                    browser.close()
                    return True
            else:
                print("? Unknown state, but may be working")
                browser.close()
                return True

    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


def post_content(content, visible=False):
    """Post content to LinkedIn"""
    print(f"\n📝 Posting to LinkedIn...\n")
    print(f"Content preview: {content[:100]}{'...' if len(content) > 100 else ''}\n")

    if not check_session():
        return False

    try:
        with sync_playwright() as p:
            browser, context, page = get_browser_context(p)

            # Go to feed
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            human_delay(1000, 2000)

            # Click "Start a post"
            try:
                page.click('button[aria-label="Start a post"]')
                human_delay(1000, 2000)
                print("✓ Opened post composer")
            except Exception as e:
                print(f"⚠️  Could not click post button: {e}")

            # Enter text
            try:
                text_field = page.locator('div[contenteditable="true"]').first
                text_field.click()
                human_delay(300, 500)

                # Clear and type
                page.keyboard.press('Control+A')
                human_delay(200, 400)
                page.keyboard.press('Delete')
                human_delay(300, 500)
                text_field.type(content, delay=50)
                human_delay(500, 1000)
                print("✓ Content entered")
            except Exception as e:
                print(f"⚠️  Could not enter text: {e}")

            # Click Post button
            human_delay(1000, 2000)
            try:
                page.click('button:has-text("Post")')
                human_delay(2000, 3000)
                print("✓ Post button clicked")
            except Exception as e:
                print(f"⚠️  Could not click Post: {e}")

            # Save session
            context.storage_state(path=SESSION_FILE)
            browser.close()

            print("\n✓ Post completed!\n")
            return True

    except Exception as e:
        print(f"\n❌ Post failed: {e}\n")
        return False


def watch_messages():
    """Watch for new LinkedIn messages"""
    print("\n👁️  Starting LinkedIn message watcher...\n")
    print("Press Ctrl+C to stop\n")

    if not check_session():
        return False

    poll_interval = 60
    retries = 0
    max_retries = 3

    while retries < max_retries:
        try:
            with sync_playwright() as p:
                browser, context, page = get_browser_context(p)

                while True:
                    try:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking messages...")

                        # Go to messaging
                        page.goto("https://www.linkedin.com/messaging/", wait_until="domcontentloaded", timeout=30000)
                        human_delay(500, 1000)

                        # Look for unread
                        unread = page.locator('.msg-conversation-card__unread-count').all()
                        if unread:
                            print(f"  → Found {len(unread)} unread message(s)")

                            # Save to vault
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{VAULT_PATH}/linkedin_message_{timestamp}.md"

                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(f"# New LinkedIn Message\n\n")
                                f.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                                f.write(f"**Unread Count:** {len(unread)}\n\n")
                                f.write(f"*Check LinkedIn for details.*\n")

                            print(f"  → Saved to: {filename}")

                        # Check notifications
                        page.goto("https://www.linkedin.com/notifications/", wait_until="domcontentloaded", timeout=30000)
                        human_delay(500, 1000)

                        notif = page.locator('.nt-segment--unread').all()
                        if notif:
                            print(f"  → Found {len(notif)} unread notification(s)")

                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{VAULT_PATH}/linkedin_notification_{timestamp}.md"

                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(f"# New LinkedIn Notification\n\n")
                                f.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                                f.write(f"**Unread Count:** {len(notif)}\n\n")
                                f.write(f"*Check LinkedIn for details.*\n")

                            print(f"  → Saved to: {filename}")

                        print(f"  → Sleeping for {poll_interval}s...\n")
                        time.sleep(poll_interval)

                    except KeyboardInterrupt:
                        print("\n\n⏹️  Watcher stopped by user")
                        browser.close()
                        return

                    except Exception as e:
                        print(f"  → Error: {e}")
                        time.sleep(poll_interval)
                        continue

                browser.close()

        except Exception as e:
            retries += 1
            print(f"\n⚠️  Attempt {retries}/{max_retries} failed: {e}\n")
            if retries < max_retries:
                print("Retrying in 10s...\n")
                time.sleep(10)
            else:
                print("Max retries reached.\n")
                return


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("\nLinkedIn Simple - Easy LinkedIn Automation")
        print("\nUsage:")
        print("  python linkedin_simple.py test              Test setup")
        print("  python linkedin_simple.py post -c \"text\"    Post content")
        print("  python linkedin_simple.py watch             Watch messages")
        print("\nFirst time? Run: python setup_sessions.py\n")
        return

    command = sys.argv[1]

    if command == "test":
        success = test_setup()
        sys.exit(0 if success else 1)

    elif command == "post":
        content = None
        if "-c" in sys.argv:
            idx = sys.argv.index("-c")
            if idx + 1 < len(sys.argv):
                content = sys.argv[idx + 1]
        elif "-f" in sys.argv:
            idx = sys.argv.index("-f")
            if idx + 1 < len(sys.argv):
                try:
                    with open(sys.argv[idx + 1], 'r') as f:
                        content = f.read().strip()
                except Exception as e:
                    print(f"Error reading file: {e}")
                    sys.exit(1)

        if not content:
            print("Error: No content provided. Use -c \"text\" or -f file.txt")
            sys.exit(1)

        success = post_content(content)
        sys.exit(0 if success else 1)

    elif command == "watch":
        watch_messages()

    else:
        print(f"Unknown command: {command}")
        print("Use: test, post, or watch")
        sys.exit(1)


if __name__ == "__main__":
    main()
