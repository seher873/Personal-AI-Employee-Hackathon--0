#!/usr/bin/env python3
"""
Twitter (X) Browser Watcher
===========================
Playwright-based watcher for Twitter mentions and replies
(no API libs, only Playwright sync)

Agent Skills:
- Browser automation with persistent sessions
- Mention/reply monitoring
- Inbox saving with timestamped files
- Ralph Wiggum retry loop
- Human-like browsing behavior

Usage:
    python twitter_browser_watcher.py [--interval 60] [--once]
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Configuration
BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "twitter_session"
INBOX_DIR = BASE_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"

# Environment variables
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

# URLs
TWITTER_LOGIN_URL = "https://twitter.com/login"
TWITTER_NOTIFICATIONS_URL = "https://twitter.com/i/notifications"
TWITTER_MENTIONS_URL = "https://twitter.com/i/notifications/mentions"
TWITTER_MESSAGES_URL = "https://twitter.com/messages"

# Timing
POLL_INTERVAL = 60  # seconds
PAGE_LOAD_TIMEOUT = 60000
ACTION_TIMEOUT = 30000
IMPLICIT_WAIT = 3000

# Ralph Wiggum Loop
MAX_RETRIES = 3
RETRY_DELAY = 2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'twitter_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TwitterWatcher')


class RalphWiggumLoop:
    """
    Agent Skill: Ralph Wiggum Retry Loop
    "Me fail English? That's unpossible!" - Keeps trying until success
    
    Provides automatic retry with exponential backoff for failed operations.
    """
    
    def __init__(self, max_retries: int = MAX_RETRIES):
        self.max_retries = max_retries
        self.current_retry = 0
    
    def reset(self):
        """Reset retry counter"""
        self.current_retry = 0
    
    def should_retry(self) -> bool:
        """
        Check if we should retry
        
        Returns: True if can retry, False if max retries exhausted
        """
        if self.current_retry < self.max_retries:
            self.current_retry += 1
            delay = RETRY_DELAY * (2 ** (self.current_retry - 1))  # Exponential backoff
            logger.info(f"🍩 Ralph Wiggum Loop: Retry {self.current_retry}/{self.max_retries} in {delay}s")
            time.sleep(delay)
            return True
        logger.error("🍩 Ralph Wiggum Loop: Max retries exhausted")
        return False


class HumanLikeBehavior:
    """
    Agent Skill: Human-like browsing behavior
    Makes automation appear more natural to avoid detection
    
    Simulates:
    - Random scrolling patterns
    - Variable delays between actions
    - Natural mouse movements
    """
    
    @staticmethod
    def random_scroll(page: Page, min_pixels: int = 50, max_pixels: int = 300) -> None:
        """
        Scroll page with human-like variability
        
        Agent Skill: Natural reading behavior simulation
        """
        scroll_amount = random.randint(min_pixels, max_pixels)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def random_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
        """Random delay between actions"""
        time.sleep(random.uniform(min_ms, max_ms) / 1000)
    
    @staticmethod
    def mouse_movement(page: Page) -> None:
        """
        Simulate natural mouse movement
        
        Agent Skill: Background mouse activity to appear human
        """
        viewport = page.viewport_size
        if viewport:
            for _ in range(random.randint(3, 7)):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))


class TwitterWatcher:
    """Monitor Twitter mentions, replies, and messages"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeBehavior()
        self.seen_items = set()
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Twitter/X
        
        Agent Skill: Multi-step login flow handling
        """
        logger.info("Logging into Twitter/X...")
        
        try:
            self.page.goto(TWITTER_LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Check if already logged in
            if "twitter.com" in self.page.url and "login" not in self.page.url.lower():
                logger.info("Already logged in to Twitter/X")
                return True
            
            # Step 1: Enter email/username
            try:
                email_field = self.page.locator('input[autocomplete="username"]').first
                email_field.fill(email)
                
                # Click Next
                next_btn = self.page.locator('div[role="button"]').filter(has_text="Next").first
                next_btn.click()
                time.sleep(3)
            except Exception as e:
                logger.debug(f"Email entry issue: {e}")
            
            # Step 2: Enter password
            password_field = self.page.locator('input[type="password"]').first
            password_field.fill(password)
            
            # Click Log in
            login_btn = self.page.locator('div[role="button"]').filter(has_text="Log in").first
            login_btn.click()
            
            # Wait for navigation
            time.sleep(5)
            self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            
            logger.info("Twitter/X login completed")
            return True
            
        except Exception as e:
            logger.error(f"Twitter/X login failed: {e}")
            return False
    
    def check_mentions(self) -> list:
        """
        Check Twitter mentions
        
        Agent Skill: Extract mention data from notifications page
        """
        logger.info("Checking Twitter mentions...")
        mentions = []
        
        try:
            self.page.goto(TWITTER_MENTIONS_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find mention notifications
            # Twitter uses various selectors, try multiple approaches
            mention_selectors = [
                'article[data-testid="tweet"]',
                'div[role="article"]',
                'article[aria-label*="mention"]'
            ]
            
            articles = []
            for selector in mention_selectors:
                try:
                    articles = self.page.locator(selector).all()
                    if articles:
                        break
                except:
                    continue
            
            for article in articles[:15]:  # Limit to 15 recent
                try:
                    content = article.inner_text()
                    
                    # Extract username if possible
                    username = ""
                    try:
                        username_elem = article.locator('[data-testid="User-Name"]').first
                        username = username_elem.inner_text()
                    except:
                        pass
                    
                    # Generate unique ID
                    mention_id = f"x_mention_{hash(content)}"
                    timestamp = datetime.now().isoformat()
                    
                    if mention_id not in self.seen_items:
                        self.seen_items.add(mention_id)
                        mentions.append({
                            'id': mention_id,
                            'source': 'twitter',
                            'type': 'mention',
                            'username': username,
                            'content': content,
                            'timestamp': timestamp,
                            'platform': 'twitter'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract mention: {e}")
            
            logger.info(f"Found {len(mentions)} new Twitter mentions")
            
        except Exception as e:
            logger.error(f"Error checking Twitter mentions: {e}")
        
        return mentions
    
    def check_replies(self) -> list:
        """
        Check Twitter replies to your tweets
        
        Agent Skill: Extract reply data from notifications
        """
        logger.info("Checking Twitter replies...")
        replies = []
        
        try:
            self.page.goto(TWITTER_NOTIFICATIONS_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find reply notifications
            articles = self.page.locator('article[data-testid="tweet"]').all()
            
            for article in articles[:15]:  # Limit to 15 recent
                try:
                    content = article.inner_text()
                    
                    # Check if it's a reply (contains "replied" or starts with @)
                    is_reply = (
                        'replied' in content.lower() or
                        content.strip().startswith('@')
                    )
                    
                    if is_reply:
                        # Extract username
                        username = ""
                        try:
                            username_elem = article.locator('[data-testid="User-Name"]').first
                            username = username_elem.inner_text()
                        except:
                            pass
                        
                        reply_id = f"x_reply_{hash(content)}"
                        timestamp = datetime.now().isoformat()
                        
                        if reply_id not in self.seen_items:
                            self.seen_items.add(reply_id)
                            replies.append({
                                'id': reply_id,
                                'source': 'twitter',
                                'type': 'reply',
                                'username': username,
                                'content': content,
                                'timestamp': timestamp,
                                'platform': 'twitter'
                            })
                except Exception as e:
                    logger.debug(f"Could not extract reply: {e}")
            
            logger.info(f"Found {len(replies)} new Twitter replies")
            
        except Exception as e:
            logger.error(f"Error checking Twitter replies: {e}")
        
        return replies
    
    def check_messages(self) -> list:
        """
        Check Twitter DMs (Direct Messages)
        
        Agent Skill: Extract DM data from messages page
        """
        logger.info("Checking Twitter messages...")
        messages = []
        
        try:
            self.page.goto(TWITTER_MESSAGES_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(5)
            
            # Human-like scrolling
            self.human.random_scroll(self.page)
            
            # Find message conversations
            conversations = self.page.locator('div[role="listitem"]').all()
            
            for conv in conversations[:10]:  # Limit to 10 recent
                try:
                    sender = ""
                    preview = ""
                    
                    try:
                        sender = conv.locator('span[dir="auto"]').first.inner_text()
                    except:
                        pass
                    
                    try:
                        preview = conv.locator('span[dir="auto"]').nth(1).inner_text()
                    except:
                        preview = conv.inner_text()
                    
                    message_id = f"x_msg_{hash(sender + preview)}"
                    timestamp = datetime.now().isoformat()
                    
                    if message_id not in self.seen_items:
                        self.seen_items.add(message_id)
                        messages.append({
                            'id': message_id,
                            'source': 'twitter',
                            'type': 'message',
                            'sender': sender,
                            'preview': preview,
                            'timestamp': timestamp,
                            'platform': 'twitter'
                        })
                except Exception as e:
                    logger.debug(f"Could not extract message: {e}")
            
            logger.info(f"Found {len(messages)} new Twitter messages")
            
        except Exception as e:
            logger.error(f"Error checking Twitter messages: {e}")
        
        return messages
    
    def take_screenshot(self, filename: str) -> str:
        """
        Take screenshot for audit
        
        Agent Skill: Visual documentation of monitoring activity
        """
        screenshots_dir = BASE_DIR / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        filepath = screenshots_dir / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


def save_to_inbox(items: list, platform: str) -> list:
    """
    Save items to Inbox directory
    
    Agent Skill: Persistent message storage in markdown format
    Creates timestamped files for each polling cycle
    """
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"new_x_{timestamp}.md"
    filepath = INBOX_DIR / filename
    
    if not items:
        return saved_files
    
    with open(filepath, 'w') as f:
        f.write(f"# Twitter (X) Activity\n\n")
        f.write(f"## Retrieved: {datetime.now().isoformat()}\n\n")
        f.write(f"## Platform: {platform}\n\n")
        f.write("---\n\n")
        
        # Group by type
        by_type = {}
        for item in items:
            item_type = item['type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        for item_type, type_items in by_type.items():
            f.write(f"## {item_type.capitalize()}s ({len(type_items)})\n\n")
            
            for item in type_items:
                f.write(f"### {item['id']}\n\n")
                f.write(f"- **Source**: {item['source']}\n")
                f.write(f"- **Platform**: {item['platform']}\n")
                f.write(f"- **Timestamp**: {item['timestamp']}\n")
                
                if 'username' in item and item['username']:
                    f.write(f"- **User**: {item['username']}\n")
                if 'sender' in item and item['sender']:
                    f.write(f"- **Sender**: {item['sender']}\n")
                if 'preview' in item and item['preview']:
                    f.write(f"- **Preview**: {item['preview']}\n")
                if 'content' in item and item['content']:
                    f.write(f"- **Content**: {item['content'][:500]}...\n" if len(item['content']) > 500 else f"- **Content**: {item['content']}\n")
                
                f.write("\n---\n\n")
    
    saved_files.append(str(filepath))
    logger.info(f"Saved {len(items)} items to {filepath}")
    
    return saved_files


def run_watcher_with_retry(watcher, check_func, label: str, ralph_loop: RalphWiggumLoop) -> list:
    """
    Run watcher function with Ralph Wiggum retry loop
    
    Agent Skill: Automatic error recovery with retry logic
    """
    ralph_loop.reset()
    
    while True:
        try:
            items = check_func()
            if items is not None:
                return items
        except Exception as e:
            logger.error(f"{label} watcher error: {e}")
        
        if not ralph_loop.should_retry():
            logger.error(f"{label} watcher failed after {ralph_loop.max_retries} retries")
            return []


def main():
    """Main entry point"""
    print("=" * 60)
    print("🐦 Twitter (X) Browser Watcher")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Monitor Twitter mentions and replies')
    parser.add_argument('--interval', type=int, default=POLL_INTERVAL,
                       help=f'Polling interval in seconds (default: {POLL_INTERVAL})')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (no continuous polling)')
    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode')
    args = parser.parse_args()
    
    print(f"⏱️  Polling interval: {args.interval}s")
    print(f"🔄 Single run: {args.once}")
    print()
    
    # Ensure directories exist
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR = BASE_DIR / "Screenshots"
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    ralph_loop = RalphWiggumLoop()
    total_items = 0
    
    with sync_playwright() as p:
        # Launch browser in persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=args.headless,  # Visible by default
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        browser.contexts[0].set_default_timeout(ACTION_TIMEOUT)
        
        page = browser.contexts[0].pages[0] if browser.contexts[0].pages else browser.contexts[0].new_page()
        twitter_watcher = TwitterWatcher(page)
        
        try:
            # Login
            print("=" * 40)
            print("🐦 Twitter Watcher")
            print("=" * 40)
            
            if TWITTER_EMAIL and TWITTER_PASSWORD:
                twitter_watcher.login(TWITTER_EMAIL, TWITTER_PASSWORD)
            else:
                logger.warning("Twitter credentials not set - using existing session")
            
            # Main polling loop
            iteration = 0
            while True:
                iteration += 1
                logger.info(f"\n📊 Polling iteration #{iteration}")
                print(f"\n{'=' * 60}")
                print(f"📊 Polling #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('=' * 60)
                
                all_items = []
                
                # Check mentions
                mentions = run_watcher_with_retry(
                    twitter_watcher, 
                    twitter_watcher.check_mentions, 
                    'Twitter Mentions', 
                    ralph_loop
                )
                all_items.extend(mentions)
                
                # Check replies
                replies = run_watcher_with_retry(
                    twitter_watcher, 
                    twitter_watcher.check_replies, 
                    'Twitter Replies', 
                    ralph_loop
                )
                all_items.extend(replies)
                
                # Check messages
                messages = run_watcher_with_retry(
                    twitter_watcher, 
                    twitter_watcher.check_messages, 
                    'Twitter Messages', 
                    ralph_loop
                )
                all_items.extend(messages)
                
                # Save to inbox
                if all_items:
                    saved_files = save_to_inbox(all_items, 'twitter')
                    total_items += len(all_items)
                    print(f"✅ Saved {len(all_items)} new items to inbox")
                    for f in saved_files:
                        print(f"   📄 {f}")
                else:
                    print("ℹ️  No new items")
                
                # Screenshot periodically
                if iteration % 10 == 0:
                    screenshot = twitter_watcher.take_screenshot(
                        f"twitter_watch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    )
                    print(f"📸 Screenshot: {screenshot}")
                
                # Single run mode
                if args.once:
                    break
                
                # Wait for next poll
                print(f"⏳ Waiting {args.interval}s for next poll...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping watcher...")
        finally:
            browser.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  Total items collected: {total_items}")
    print(f"  Inbox directory: {INBOX_DIR}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
