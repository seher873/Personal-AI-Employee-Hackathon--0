#!/usr/bin/env python3
"""
Facebook & Instagram Browser Watcher
====================================
Playwright-based watcher for FB/IG messages and comments
(no API libs, only Playwright sync)

Agent Skills:
- Browser automation with persistent sessions
- Message/comment monitoring
- Inbox saving with timestamped files
- Ralph Wiggum retry loop
- Human-like browsing behavior

Usage:
    python fb_ig_browser_watcher.py [--platform fb|ig|both] [--interval 60]
"""

import os
import sys
import time
import random
import logging
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, BrowserContext # type: ignore

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "fb_ig_session"
INBOX_DIR = BASE_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"

# Environment variables
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")

# URLs
FB_MESSAGES_URL = "https://www.facebook.com/messages"
FB_NOTIFICATIONS_URL = "https://www.facebook.com/notifications"
IG_MESSAGES_URL = "https://www.instagram.com/direct/inbox/"
IG_NOTIFICATIONS_URL = "https://www.instagram.com/accounts/activity/"

# Timing
POLL_INTERVAL = 60  # seconds
PAGE_LOAD_TIMEOUT = 120000  # 2 minutes for page load
ACTION_TIMEOUT = 90000  # 90 seconds for actions
IMPLICIT_WAIT = 10000  # 10 seconds implicit wait
LOGIN_WAIT = 15  # 15 seconds wait after login click

# Ralph Wiggum Loop
MAX_RETRIES = 3
RETRY_DELAY = 2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'fb_ig_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FBIGWatcher')


class RalphWiggumLoop:
    """
    Agent Skill: Ralph Wiggum Retry Loop
    "Me fail English? That's unpossible!" - Keeps trying until success
    """
    
    def __init__(self, max_retries: int = MAX_RETRIES):
        self.max_retries = max_retries
        self.current_retry = 0
    
    def reset(self):
        self.current_retry = 0
    
    def should_retry(self) -> bool:
        """Check if we should retry"""
        if self.current_retry < self.max_retries:
            self.current_retry += 1
            delay = RETRY_DELAY * (2 ** (self.current_retry - 1))
            logger.info(f"🍩 Ralph Wiggum Loop: Retry {self.current_retry}/{self.max_retries} in {delay}s")
            time.sleep(delay)
            return True
        logger.error("🍩 Ralph Wiggum Loop: Max retries exhausted")
        return False


class HumanLikeBehavior:
    """
    Agent Skill: Human-like browsing behavior
    Makes automation appear more natural
    """
    
    @staticmethod
    def random_scroll(page: Page, min_pixels: int = 50, max_pixels: int = 300) -> None:
        """Scroll page with human-like variability"""
        scroll_amount = random.randint(min_pixels, max_pixels)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def random_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
        """Random delay between actions"""
        time.sleep(random.uniform(min_ms, max_ms) / 1000)
    
    @staticmethod
    def mouse_movement(page: Page) -> None:
        """Simulate natural mouse movement"""
        viewport = page.viewport_size
        if viewport:
            for _ in range(random.randint(3, 7)):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))


class FacebookWatcher:
    """Monitor Facebook messages and comments"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeBehavior()
        self.seen_items = set()
    
    def login(self, email: str, password: str) -> bool:
        """Login to Facebook"""
        logger.info("Logging into Facebook...")

        try:
            self.page.goto("https://www.facebook.com/login", timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)

            # Check if already logged in
            if "facebook.com" in self.page.url and "login" not in self.page.url.lower():
                logger.info("Already logged in to Facebook")
                return True

            # Wait for login form to be ready
            self.page.wait_for_selector('#email', timeout=PAGE_LOAD_TIMEOUT)
            
            # Fill credentials
            self.page.fill('#email', email)
            self.page.fill('#pass', password)
            time.sleep(2)

            # Click login
            self.page.click('button[name="login"]')
            logger.info("Login button clicked, waiting for page to load...")
            
            # Wait longer for login to complete
            time.sleep(LOGIN_WAIT)
            
            # Wait for navigation or network idle
            try:
                self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            except:
                pass
            
            time.sleep(5)
            
            logger.info(f"Facebook login completed. Current URL: {self.page.url}")
            return True

        except Exception as e:
            logger.error(f"Facebook login failed: {e}")
            return False
    
    def check_messages(self) -> list:
        """
        Check Facebook messages
        
        Agent Skill: Extract message data from page
        """
        logger.info("Checking Facebook messages...")
        messages = []
        
        try:
            self.page.goto(FB_MESSAGES_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find message threads
            message_threads = self.page.locator('div[role="row"]').all()
            
            for thread in message_threads[:10]:  # Limit to 10 recent
                try:
                    sender = thread.locator('span[dir="auto"]').first.inner_text()
                    preview = thread.locator('span[dir="auto"]').nth(1).inner_text() if thread.locator('span[dir="auto"]').count() > 1 else ""
                    timestamp = datetime.now().isoformat()
                    
                    message_id = f"fb_msg_{hash(sender + preview)}"
                    
                    if message_id not in self.seen_items:
                        self.seen_items.add(message_id)
                        messages.append({
                            'id': message_id,
                            'source': 'facebook',
                            'type': 'message',
                            'sender': sender,
                            'preview': preview,
                            'timestamp': timestamp,
                            'platform': 'facebook'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract message: {e}")
            
            logger.info(f"Found {len(messages)} new Facebook messages")
            
        except Exception as e:
            logger.error(f"Error checking Facebook messages: {e}")
        
        return messages
    
    def check_comments(self) -> list:
        """
        Check Facebook comments/notifications
        
        Agent Skill: Extract comment data from notifications
        """
        logger.info("Checking Facebook comments...")
        comments = []
        
        try:
            self.page.goto(FB_NOTIFICATIONS_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find notifications
            notifications = self.page.locator('div[role="article"]').all()
            
            for notif in notifications[:10]:  # Limit to 10 recent
                try:
                    content = notif.inner_text()
                    timestamp = datetime.now().isoformat()
                    
                    # Check if it's a comment
                    if any(kw in content.lower() for kw in ['commented', 'replied', 'mentioned']):
                        notif_id = f"fb_comment_{hash(content)}"
                        
                        if notif_id not in self.seen_items:
                            self.seen_items.add(notif_id)
                            comments.append({
                                'id': notif_id,
                                'source': 'facebook',
                                'type': 'comment',
                                'content': content,
                                'timestamp': timestamp,
                                'platform': 'facebook'
                            })
                except Exception as e:
                    logger.debug(f"Could not extract notification: {e}")
            
            logger.info(f"Found {len(comments)} new Facebook comments")
            
        except Exception as e:
            logger.error(f"Error checking Facebook comments: {e}")
        
        return comments
    
    def take_screenshot(self, filename: str) -> str:
        """Take screenshot for audit"""
        screenshots_dir = BASE_DIR / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        filepath = screenshots_dir / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


class InstagramWatcher:
    """Monitor Instagram messages and comments"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeBehavior()
        self.seen_items = set()
    
    def login(self, username: str, password: str) -> bool:
        """Login to Instagram"""
        logger.info("Logging into Instagram...")
        
        try:
            self.page.goto(IG_LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Check if already logged in
            if "instagram.com" in self.page.url and "login" not in self.page.url:
                logger.info("Already logged in to Instagram")
                return True
            
            # Handle cookie consent
            try:
                cookie_btn = self.page.locator('button').filter(has_text="Allow all cookies").first
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    time.sleep(2)
            except:
                pass
            
            # Fill credentials
            self.page.fill('input[name="username"]', username)
            self.page.fill('input[name="password"]', password)
            
            # Click login
            self.page.click('button[type="submit"]')
            time.sleep(5)
            self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            
            # Handle "Save login info"
            try:
                not_now = self.page.locator('button').filter(has_text="Not Now").first
                if not_now.is_visible():
                    not_now.click()
                    time.sleep(2)
            except:
                pass
            
            logger.info("Instagram login completed")
            return True
            
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False
    
    def check_messages(self) -> list:
        """
        Check Instagram direct messages
        
        Agent Skill: Extract DM data from page
        """
        logger.info("Checking Instagram messages...")
        messages = []
        
        try:
            self.page.goto(IG_MESSAGES_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find message threads
            message_threads = self.page.locator('div[role="listitem"]').all()
            
            for thread in message_threads[:10]:  # Limit to 10 recent
                try:
                    sender = thread.locator('span[dir="auto"]').first.inner_text()
                    preview = thread.locator('span[dir="auto"]').nth(1).inner_text() if thread.locator('span[dir="auto"]').count() > 1 else ""
                    timestamp = datetime.now().isoformat()
                    
                    message_id = f"ig_msg_{hash(sender + preview)}"
                    
                    if message_id not in self.seen_items:
                        self.seen_items.add(message_id)
                        messages.append({
                            'id': message_id,
                            'source': 'instagram',
                            'type': 'message',
                            'sender': sender,
                            'preview': preview,
                            'timestamp': timestamp,
                            'platform': 'instagram'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract message: {e}")
            
            logger.info(f"Found {len(messages)} new Instagram messages")
            
        except Exception as e:
            logger.error(f"Error checking Instagram messages: {e}")
        
        return messages
    
    def check_comments(self) -> list:
        """
        Check Instagram comments/notifications
        
        Agent Skill: Extract comment data from activity page
        """
        logger.info("Checking Instagram comments...")
        comments = []
        
        try:
            self.page.goto(IG_NOTIFICATIONS_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find notifications
            notifications = self.page.locator('div[role="listitem"]').all()
            
            for notif in notifications[:10]:  # Limit to 10 recent
                try:
                    content = notif.inner_text()
                    timestamp = datetime.now().isoformat()
                    
                    # Check if it's a comment
                    if any(kw in content.lower() for kw in ['comment', 'reply', 'mention', 'tagged']):
                        notif_id = f"ig_comment_{hash(content)}"
                        
                        if notif_id not in self.seen_items:
                            self.seen_items.add(notif_id)
                            comments.append({
                                'id': notif_id,
                                'source': 'instagram',
                                'type': 'comment',
                                'content': content,
                                'timestamp': timestamp,
                                'platform': 'instagram'
                            })
                except Exception as e:
                    logger.debug(f"Could not extract notification: {e}")
            
            logger.info(f"Found {len(comments)} new Instagram comments")
            
        except Exception as e:
            logger.error(f"Error checking Instagram comments: {e}")
        
        return comments
    
    def take_screenshot(self, filename: str) -> str:
        """Take screenshot for audit"""
        screenshots_dir = BASE_DIR / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        filepath = screenshots_dir / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


def save_to_inbox(items: list, platform: str) -> list:
    """
    Save items to Inbox directory
    
    Agent Skill: Persistent message storage
    """
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"new_fb_ig_{timestamp}.md"
    filepath = INBOX_DIR / filename
    
    if not items:
        return saved_files
    
    with open(filepath, 'w') as f:
        f.write(f"# {platform.capitalize()} Messages/Comments\n\n")
        f.write(f"## Retrieved: {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        
        for item in items:
            f.write(f"### {item['type'].capitalize()}: {item['id']}\n\n")
            f.write(f"- **Source**: {item['source']}\n")
            f.write(f"- **Platform**: {item['platform']}\n")
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


def run_watcher_with_retry(watcher, check_func, platform: str, ralph_loop: RalphWiggumLoop) -> list:
    """Run watcher function with Ralph Wiggum retry loop"""
    ralph_loop.reset()
    
    while True:
        try:
            items = check_func()
            if items is not None:
                return items
        except Exception as e:
            logger.error(f"{platform} watcher error: {e}")
        
        if not ralph_loop.should_retry():
            logger.error(f"{platform} watcher failed after {ralph_loop.max_retries} retries")
            return []


def main():
    """Main entry point"""
    print("=" * 60)
    print("📱 Facebook & Instagram Browser Watcher")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', type=str, choices=['fb', 'ig', 'both'], default='both',
                       help='Platform to monitor')
    parser.add_argument('--interval', type=int, default=POLL_INTERVAL,
                       help=f'Polling interval in seconds (default: {POLL_INTERVAL})')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (no continuous polling)')
    args = parser.parse_args()
    
    print(f"🎯 Platform: {args.platform}")
    print(f"⏱️  Polling interval: {args.interval}s")
    print(f"🔄 Single run: {args.once}")
    print()
    
    # Ensure directories exist
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    ralph_loop = RalphWiggumLoop()
    total_items = 0
    
    with sync_playwright() as p:
        # Launch browser in persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # Headless mode
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--start-maximized'
            ],
            timeout=PAGE_LOAD_TIMEOUT
        )

        context.set_default_timeout(ACTION_TIMEOUT)
        
        try:
            # Facebook watcher
            fb_page = None
            fb_watcher = None
            if args.platform in ['fb', 'both']:
                print("\n" + "=" * 40)
                print("📘 Facebook Watcher")
                print("=" * 40)

                fb_page = context.new_page()
                fb_watcher = FacebookWatcher(fb_page)
                
                if FB_EMAIL and FB_PASSWORD:
                    fb_watcher.login(FB_EMAIL, FB_PASSWORD)
                else:
                    logger.warning("Facebook credentials not set")
            
            # Instagram watcher
            ig_page = None
            ig_watcher = None
            if args.platform in ['ig', 'both']:
                print("\n" + "=" * 40)
                print("📷 Instagram Watcher")
                print("=" * 40)

                ig_page = context.new_page()
                ig_watcher = InstagramWatcher(ig_page)
                
                if IG_USERNAME and IG_PASSWORD:
                    ig_watcher.login(IG_USERNAME, IG_PASSWORD)
                else:
                    logger.warning("Instagram credentials not set")
            
            # Main polling loop
            iteration = 0
            while True:
                iteration += 1
                logger.info(f"\n📊 Polling iteration #{iteration}")
                print(f"\n{'=' * 60}")
                print(f"📊 Polling #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('=' * 60)
                
                all_items = []
                
                # Check Facebook
                if fb_watcher and args.platform in ['fb', 'both']:
                    messages = run_watcher_with_retry(fb_watcher, fb_watcher.check_messages, 'Facebook', ralph_loop)
                    comments = run_watcher_with_retry(fb_watcher, fb_watcher.check_comments, 'Facebook', ralph_loop)
                    all_items.extend(messages + comments)
                    
                    # Screenshot periodically
                    if iteration % 10 == 0:
                        fb_watcher.take_screenshot(f"fb_watch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                # Check Instagram
                if ig_watcher and args.platform in ['ig', 'both']:
                    messages = run_watcher_with_retry(ig_watcher, ig_watcher.check_messages, 'Instagram', ralph_loop)
                    comments = run_watcher_with_retry(ig_watcher, ig_watcher.check_comments, 'Instagram', ralph_loop)
                    all_items.extend(messages + comments)
                    
                    # Screenshot periodically
                    if iteration % 10 == 0:
                        ig_watcher.take_screenshot(f"ig_watch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                # Save to inbox
                if all_items:
                    platform_name = args.platform if args.platform != 'both' else 'fb_ig'
                    saved_files = save_to_inbox(all_items, platform_name)
                    total_items += len(all_items)
                    print(f"✅ Saved {len(all_items)} new items to inbox")
                else:
                    print("ℹ️  No new items")
                
                # Single run mode
                if args.once:
                    logger.info("✅ Single run completed. Browser will stay open for 60 seconds for verification...")
                    print("✅ Single run completed. Browser will stay open for 60 seconds...")
                    time.sleep(60)  # Keep browser open for verification
                    break
                
                # Wait for next poll
                print(f"⏳ Waiting {args.interval}s for next poll...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping watcher...")
        finally:
            context.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  Total items collected: {total_items}")
    print(f"  Inbox directory: {INBOX_DIR}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
