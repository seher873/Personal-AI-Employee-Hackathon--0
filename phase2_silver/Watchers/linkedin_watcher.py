#!/usr/bin/env python3
"""
LinkedIn Watcher
================
Monitor LinkedIn notifications, messages, and interactions

Agent Skills:
- Browser automation with persistent sessions
- Notification monitoring
- Inbox saving with timestamped files

Usage:
    python linkedin_watcher.py [--interval 60] [--once]
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "linkedin_session"
INBOX_DIR = BASE_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"

# Environment variables
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

# URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_NOTIFICATIONS_URL = "https://www.linkedin.com/notifications"
LINKEDIN_MESSAGING_URL = "https://www.linkedin.com/messaging"

# Timing
POLL_INTERVAL = 60
PAGE_LOAD_TIMEOUT = 60000
ACTION_TIMEOUT = 30000
LOGIN_TIMEOUT = 120  # seconds for manual login

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'linkedin_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInWatcher')


class LinkedInWatcher:
    """Monitor LinkedIn notifications and messages"""

    def __init__(self, page: Page):
        self.page = page
        self.seen_items = set()

    def login(self, email: str, password: str, quick_check: bool = False, force_manual: bool = False) -> bool:
        """Login to LinkedIn"""
        logger.info("Logging into LinkedIn...")
        print("🔐 LinkedIn Login: Loading...")

        max_retries = 3
        retry_delay = 10

        for attempt in range(1, max_retries + 1):
            try:
                if quick_check:
                    self.page.goto("https://www.linkedin.com", timeout=15000)
                    time.sleep(2)
                    logger.info("✅ LinkedIn browser check successful")
                    return True

                self.page.goto(LINKEDIN_LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
                time.sleep(3)

                # Check if already logged in
                if self._is_logged_in():
                    logger.info("✅ Already logged in to LinkedIn")
                    print("✅ Already logged in!")
                    return True

                # Force manual login on first attempt
                if force_manual or attempt == 1:
                    print("\n" + "=" * 60)
                    print("🖐️  MANUAL LOGIN REQUIRED")
                    print("📱 Please log in manually in the browser window")
                    print(f"⏱️  You have {LOGIN_TIMEOUT} seconds to complete login")
                    print("🔐 Enter credentials, solve captcha, or complete 2FA")
                    print("=" * 60)

                    start_time = time.time()
                    while time.time() - start_time < LOGIN_TIMEOUT:
                        time.sleep(2)
                        if self._is_logged_in():
                            print("✅ Login detected! Verifying...")
                            time.sleep(3)
                            break
                        remaining = int(LOGIN_TIMEOUT - (time.time() - start_time))
                        if remaining % 30 == 0 and remaining > 0:
                            print(f"⏱️  {remaining} seconds remaining...")

                    if self._is_logged_in():
                        logger.info("✅ LinkedIn manual login successful")
                        print("✅ Logged in successfully!")
                        return True
                    else:
                        print("⚠️  Manual login not completed, trying auto-login...")

                # Auto-login with credentials
                if email and password:
                    print("📝 Attempting auto-login...")
                    try:
                        self.page.fill('#username', email)
                        self.page.fill('#password', password)
                        self.page.click('button[type="submit"]')
                        time.sleep(5)
                        self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
                    except Exception as e:
                        logger.debug(f"Auto-login issue: {e}")

                    # Wait for manual verification if needed
                    if not self._is_logged_in():
                        print("\n" + "=" * 60)
                        print("⚠️  2FA/VERIFICATION NEEDED!")
                        print(f"⏱️  You have {LOGIN_TIMEOUT} seconds")
                        print("=" * 60)

                        start_time = time.time()
                        while time.time() - start_time < LOGIN_TIMEOUT:
                            time.sleep(2)
                            if self._is_logged_in():
                                print("✅ Verification complete!")
                                time.sleep(3)
                                break
                            remaining = int(LOGIN_TIMEOUT - (time.time() - start_time))
                            if remaining % 30 == 0 and remaining > 0:
                                print(f"⏱️  {remaining} seconds remaining...")

                if self._is_logged_in():
                    logger.info("✅ LinkedIn login successful")
                    print("✅ Logged in successfully!")
                    return True
                else:
                    logger.warning(f"❌ LinkedIn login attempt {attempt} failed")
                    print(f"❌ Login attempt {attempt} failed")

                    if attempt < max_retries:
                        print(f"⏳ Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)

            except Exception as e:
                logger.error(f"LinkedIn login attempt {attempt} failed: {e}")
                print(f"❌ Login error: {e}")

                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)

        logger.error("❌ LinkedIn login failed after all retries")
        print("❌ Login failed – check credentials, network, or 2FA")
        return False

    def _is_logged_in(self) -> bool:
        """Check if logged in to LinkedIn"""
        try:
            if "login" in self.page.url.lower():
                return False

            logged_in_selectors = [
                'div[data-testid="MessagingIcon"]',
                'div[data-testid="NotificationsIcon"]',
                'img[data-testid="MeDropdown"]',
            ]

            for selector in logged_in_selectors:
                try:
                    if self.page.locator(selector).first.is_visible(timeout=3000):
                        return True
                except:
                    continue

            return False
        except:
            return False

    def check_notifications(self) -> list:
        """Check LinkedIn notifications"""
        logger.info("Checking LinkedIn notifications...")
        notifications = []

        try:
            self.page.goto(LINKEDIN_NOTIFICATIONS_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)

            # Find notifications
            notifs = self.page.locator('div.notification-item').all()

            for notif in notifs[:15]:
                try:
                    content = notif.inner_text()
                    notif_id = f"li_notif_{hash(content)}"
                    timestamp = datetime.now().isoformat()

                    if notif_id not in self.seen_items:
                        self.seen_items.add(notif_id)
                        notifications.append({
                            'id': notif_id,
                            'source': 'linkedin',
                            'type': 'notification',
                            'content': content,
                            'timestamp': timestamp,
                            'platform': 'linkedin'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract notification: {e}")

            logger.info(f"Found {len(notifications)} new LinkedIn notifications")

        except Exception as e:
            logger.error(f"Error checking LinkedIn notifications: {e}")

        return notifications

    def check_messages(self) -> list:
        """Check LinkedIn messages"""
        logger.info("Checking LinkedIn messages...")
        messages = []

        try:
            self.page.goto(LINKEDIN_MESSAGING_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)

            # Find conversations
            convos = self.page.locator('div.conversation-card').all()

            for convo in convos[:10]:
                try:
                    name_elem = convo.locator('span.entity-result__title-line').first
                    name = name_elem.inner_text() if name_elem else "Unknown"

                    preview_elem = convo.locator('div.entity-result__subtitle-line').first
                    preview = preview_elem.inner_text() if preview_elem else ""

                    msg_id = f"li_msg_{hash(name + preview)}"
                    timestamp = datetime.now().isoformat()

                    if msg_id not in self.seen_items:
                        self.seen_items.add(msg_id)
                        messages.append({
                            'id': msg_id,
                            'source': 'linkedin',
                            'type': 'message',
                            'sender': name,
                            'preview': preview,
                            'timestamp': timestamp,
                            'platform': 'linkedin'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract message: {e}")

            logger.info(f"Found {len(messages)} new LinkedIn messages")

        except Exception as e:
            logger.error(f"Error checking LinkedIn messages: {e}")

        return messages


def save_to_inbox(items: list) -> list:
    """Save items to Inbox directory"""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"new_linkedin_{timestamp}.md"
    filepath = INBOX_DIR / filename

    if not items:
        return saved_files

    with open(filepath, 'w') as f:
        f.write(f"# LinkedIn Activity\n\n")
        f.write(f"## Retrieved: {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")

        for item in items:
            f.write(f"### {item['id']}\n\n")
            f.write(f"- **Source**: {item['source']}\n")
            f.write(f"- **Type**: {item['type']}\n")
            f.write(f"- **Timestamp**: {item['timestamp']}\n")

            if 'sender' in item:
                f.write(f"- **Sender**: {item['sender']}\n")
            if 'preview' in item:
                f.write(f"- **Preview**: {item['preview']}\n")
            if 'content' in item:
                f.write(f"- **Content**: {item['content']}\n")

            f.write("\n---\n\n")

    saved_files.append(str(filepath))
    logger.info(f"Saved {len(items)} items to {filepath}")

    return saved_files


def main():
    """Main entry point"""
    print("=" * 60)
    print("💼 LinkedIn Browser Watcher")
    print("=" * 60)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=POLL_INTERVAL,
                       help=f'Polling interval in seconds (default: {POLL_INTERVAL})')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode')
    parser.add_argument('--force-login', action='store_true',
                       help='Force fresh login')
    args = parser.parse_args()

    # Ensure directories exist
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    total_items = 0

    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_DIR),
                headless=args.headless,
                timeout=30000,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--lang=en-US'
                ]
            )
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            print(f"❌ Failed to launch browser: {e}")
            return 1

        context.set_default_timeout(ACTION_TIMEOUT)
        page = context.pages[0] if context.pages else context.new_page()
        watcher = LinkedInWatcher(page)

        try:
            # Login
            print("=" * 40)
            print("💼 LinkedIn Watcher")
            print("=" * 40)

            if LINKEDIN_EMAIL and LINKEDIN_PASSWORD and not args.once:
                success = watcher.login(LINKEDIN_EMAIL, LINKEDIN_PASSWORD, force_manual=args.force_login)
                if not success:
                    logger.warning("LinkedIn login failed - continuing anyway")
            else:
                logger.warning("LinkedIn credentials not set")
                if args.once:
                    watcher.login("", "", quick_check=True)

            # Main loop
            iteration = 0
            while True:
                iteration += 1
                logger.info(f"\n📊 Polling iteration #{iteration}")
                print(f"\n{'=' * 60}")
                print(f"📊 Polling #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('=' * 60)

                all_items = []

                notifications = watcher.check_notifications()
                all_items.extend(notifications)

                messages = watcher.check_messages()
                all_items.extend(messages)

                if all_items:
                    saved_files = save_to_inbox(all_items)
                    total_items += len(all_items)
                    print(f"✅ Saved {len(all_items)} new items to inbox")
                else:
                    print("ℹ️  No new items")

                if args.once:
                    logger.info("✅ Single run completed")
                    print("✅ Single run completed. Browser will stay open for 60 seconds...")
                    time.sleep(60)
                    break

                print(f"⏳ Waiting {args.interval}s for next poll...")
                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\n👋 Stopping watcher...")
        finally:
            context.close()

    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  Total items collected: {total_items}")
    print(f"  Inbox directory: {INBOX_DIR}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
