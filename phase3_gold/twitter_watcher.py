"""
Twitter/X Browser Watcher
Gold Tier - Monitors DMs and mentions, saves to Inbox

Checks every 60 seconds for new messages and mentions.
Saves to Inbox/ folder for processing.

Usage:
    py twitter_watcher.py
    py twitter_watcher.py --interval 60
"""

import os
import sys
import time
import random
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("[ERROR] Playwright not installed. Run: py -m pip install playwright")
    print("[INFO] Then: playwright install chromium")
    sys.exit(1)

from config import TWITTER_EMAIL, TWITTER_PASSWORD

# Configuration
CHECK_INTERVAL = 60
INBOX_DIR = "./Inbox"
SESSION_DIR = "./twitter_session"
LOGS_DIR = "./Logs"

# Create directories
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class TwitterWatcher:
    """Twitter/X Message Watcher."""
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.message_count = 0
        self.errors = 0
        self.processed_tweets = set()
        
    def _log(self, message):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(LOGS_DIR, f"twitter_watcher_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_to_inbox(self, content_type, sender, message_text):
        """Save to Inbox folder."""
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_twitter_{content_type}_{sender.replace('@', '')[:10]}.md"
        filepath = os.path.join(INBOX_DIR, filename)
        
        content = f"""---
created: {timestamp.isoformat()}
source: twitter
type: {content_type}
sender: {sender}
status: pending
---

# {content_type.title()} from {sender}

"{message_text}"

## Action Required
- Classify: Business domain
- Auto-reply or manual response
- Route: Social media team
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log(f"[INBOX] Saved: {filename}")
            self.message_count += 1
            self._save_audit(content_type, sender, message_text[:100], True)
            
        except Exception as e:
            self._log(f"[ERROR] Failed to save: {e}")
            self._save_audit(content_type, sender, message_text[:100], False, str(e))
    
    def _save_audit(self, ctype, sender, details, success, error=None):
        """Save audit log."""
        audit_file = os.path.join(LOGS_DIR, "twitter_watcher_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": f"twitter_{ctype}",
            "sender": sender,
            "details": details,
            "success": success,
            "error": error
        }
        
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def launch_browser(self):
        """Launch browser with persistent session."""
        self._log("[BROWSER] Launching Chromium...")
        
        playwright = sync_playwright().start()
        
        self.browser = playwright.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        self._log("[BROWSER] Launched")
    
    def close_browser(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
            self._log("[BROWSER] Closed")
    
    def check_dms(self):
        """Check Twitter Direct Messages."""
        self._log("[TW] Checking DMs...")
        
        try:
            self.page = self.browser.new_page()
            self.page.goto("https://twitter.com/messages", timeout=60000)
            self.page.wait_for_timeout(5000)
            
            # Check if logged in
            if "login" in self.page.url.lower():
                self._log("[TW] Not logged in, attempting login...")
                self.twitter_login()
            
            # Look for message conversations
            try:
                conversations = self.page.query_selector_all('div[role="listitem"]')
                
                if conversations:
                    self._log(f"[TW] Found {len(conversations)} DM conversations")
                    
                    for conv in conversations[:5]:
                        try:
                            sender_elem = conv.query_selector('span[dir="auto"]')
                            message_elem = conv.query_selector('span[dir="auto"] + span')
                            
                            if sender_elem and message_elem:
                                sender = sender_elem.inner_text()
                                message = message_elem.inner_text()
                                
                                self._log(f"[TW] DM from {sender}: {message[:50]}...")
                                self._save_to_inbox("dm", sender, message)
                                
                        except:
                            continue
                else:
                    self._log("[TW] No DM conversations found")
                    
            except Exception as e:
                self._log(f"[TW] Error checking DMs: {e}")
            
            self.page.close()
            self._log("[TW] DM check complete")
            
        except Exception as e:
            self._log(f"[TW] DM Error: {e}")
            self.errors += 1
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
    
    def check_mentions(self):
        """Check Twitter mentions."""
        self._log("[TW] Checking mentions...")
        
        try:
            self.page = self.browser.new_page()
            self.page.goto("https://twitter.com/notifications", timeout=60000)
            self.page.wait_for_timeout(5000)
            
            # Look for mention notifications
            try:
                # Find mentions (simplified selector)
                mentions = self.page.query_selector_all('article[data-testid="tweet"]')
                
                if mentions:
                    self._log(f"[TW] Found {len(mentions)} recent tweets/mentions")
                    
                    for mention in mentions[:5]:
                        try:
                            # Extract username
                            user_elem = mention.query_selector('a[role="link"]')
                            tweet_elem = mention.query_selector('div[data-testid="tweetText"]')
                            
                            if user_elem and tweet_elem:
                                username = user_elem.get_attribute('href', '').replace('/', '')
                                tweet_text = tweet_elem.inner_text()[:200]
                                
                                tweet_id = f"{username}_{len(tweet_text)}"
                                
                                if tweet_id not in self.processed_tweets:
                                    self._log(f"[TW] Mention from @{username}: {tweet_text[:50]}...")
                                    self._save_to_inbox("mention", f"@{username}", tweet_text)
                                    self.processed_tweets.add(tweet_id)
                                    
                        except:
                            continue
                else:
                    self._log("[TW] No mentions found")
                    
            except Exception as e:
                self._log(f"[TW] Error checking mentions: {e}")
            
            self.page.close()
            self._log("[TW] Mention check complete")
            
        except Exception as e:
            self._log(f"[TW] Mention Error: {e}")
            self.errors += 1
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
    
    def twitter_login(self):
        """Login to Twitter."""
        try:
            self.page.goto("https://twitter.com/login", timeout=60000)
            self.page.wait_for_timeout(3000)
            
            # Fill credentials
            self.page.fill('input[autocomplete="username"]', TWITTER_EMAIL)
            self.page.click('button[type="submit"]')
            self.page.wait_for_timeout(3000)
            
            self.page.fill('input[type="password"]', TWITTER_PASSWORD)
            self.page.click('button[type="submit"]')
            
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(5000)
            
            self._log("[TW] Login attempt complete")
            
        except Exception as e:
            self._log(f"[TW] Login failed: {e}")
            self.errors += 1
    
    def watch(self):
        """Main watch loop."""
        self._log("=" * 60)
        self._log("🐦 Twitter/X Watcher Started")
        self._log(f"[CONFIG] Check interval: {CHECK_INTERVAL}s")
        self._log("=" * 60)
        
        self.launch_browser()
        
        try:
            while True:
                # Check DMs
                self.check_dms()
                
                time.sleep(5)
                
                # Check mentions
                self.check_mentions()
                
                # Wait
                actual_interval = CHECK_INTERVAL + random.randint(-5, 5)
                self._log(f"[WAIT] Next check in {actual_interval}s...")
                time.sleep(actual_interval)
                
        except KeyboardInterrupt:
            self._log("[STOP] User interrupted")
        except Exception as e:
            self._log(f"[ERROR] Watcher crashed: {e}")
            self.errors += 1
        finally:
            self.close_browser()
            self._log("=" * 60)
            self._log(f"📊 Stats: {self.message_count} messages, {self.errors} errors")
            self._log("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter Watcher")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL, help="Check interval")
    args = parser.parse_args()
    
    CHECK_INTERVAL = args.interval
    
    watcher = TwitterWatcher()
    watcher.watch()
