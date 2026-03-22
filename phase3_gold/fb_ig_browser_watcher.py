"""
Facebook & Instagram Browser Watcher
Gold Tier - Monitors messages and comments, saves to Inbox

Checks every 60 seconds for new messages on Facebook Page and Instagram.
Saves new messages to Inbox/ folder for processing.

Usage:
    py fb_ig_browser_watcher.py
    py fb_ig_browser_watcher.py --interval 60
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

from config import FB_EMAIL, FB_PASSWORD, IG_USERNAME, IG_PASSWORD

# Configuration
CHECK_INTERVAL = 60  # seconds
INBOX_DIR = "./Inbox"
SESSION_DIR = "./fb_ig_session"
LOGS_DIR = "./Logs"

# Create directories
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class FBIGWatcher:
    """Facebook and Instagram Message Watcher."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.last_message_time = None
        self.message_count = 0
        self.errors = 0
        
    def _log(self, message):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Save to log file
        log_file = os.path.join(LOGS_DIR, f"fb_ig_watcher_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_to_inbox(self, source, sender, message_text, message_id=None):
        """Save message to Inbox folder."""
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{source}_{sender.replace('+', '')[:10]}.md"
        filepath = os.path.join(INBOX_DIR, filename)
        
        content = f"""---
created: {timestamp.isoformat()}
source: {source}
sender: {sender}
status: pending
message_id: {message_id or 'N/A'}
---

# Message from {sender}

"{message_text}"

## Action Required
- Classify: Business domain
- Auto-reply: Check keywords
- Route: Social media response
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log(f"[INBOX] Saved: {filename}")
            self.message_count += 1
            
            # Save audit log
            self._save_audit(source, sender, message_text[:100], True)
            
        except Exception as e:
            self._log(f"[ERROR] Failed to save message: {e}")
            self._save_audit(source, sender, message_text[:100], False, str(e))
    
    def _save_audit(self, source, sender, details, success, error=None):
        """Save audit log entry."""
        audit_file = os.path.join(LOGS_DIR, "fb_ig_watcher_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "message_detected",
            "source": source,
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
        
        # Launch with persistent user data
        self.browser = playwright.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,  # Show browser for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        self._log("[BROWSER] Launched with persistent session")
    
    def close_browser(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
            self._log("[BROWSER] Closed")
    
    def check_facebook_messages(self):
        """Check Facebook Page messages."""
        self._log("[FB] Checking messages...")
        
        try:
            # Go to Facebook Page inbox
            page_url = f"https://www.facebook.com/{FB_PAGE_ID}/messages/"
            
            self.page = self.browser.new_page()
            self.page.goto(page_url, timeout=60000)
            
            # Wait for page to load
            self.page.wait_for_timeout(5000)
            
            # Check if logged in
            if "login" in self.page.url.lower():
                self._log("[FB] Not logged in, attempting login...")
                self.facebook_login()
            
            # Look for message threads
            try:
                # Find message threads (selectors may need adjustment)
                message_threads = self.page.query_selector_all('div[role="row"]')
                
                if message_threads:
                    self._log(f"[FB] Found {len(message_threads)} message threads")
                    
                    # Check first few threads for new messages
                    for thread in message_threads[:5]:
                        try:
                            sender_elem = thread.query_selector('span[dir="auto"]')
                            message_elem = thread.query_selector('span[dir="auto"] + span')
                            time_elem = thread.query_selector('span[title]')
                            
                            if sender_elem and message_elem:
                                sender = sender_elem.inner_text()
                                message = message_elem.inner_text()
                                time_str = time_elem.get_attribute('title') if time_elem else "Unknown"
                                
                                # Check if this is a new message
                                if self.is_new_message(sender, message):
                                    self._log(f"[FB] New message from {sender}: {message[:50]}...")
                                    self._save_to_inbox("facebook", sender, message)
                                    
                        except Exception as e:
                            continue  # Skip problematic threads
                
                else:
                    self._log("[FB] No message threads found")
                    
            except Exception as e:
                self._log(f"[FB] Error checking messages: {e}")
            
            self.page.close()
            self._log("[FB] Check complete")
            
        except Exception as e:
            self._log(f"[FB] Error: {e}")
            self.errors += 1
    
    def check_instagram_messages(self):
        """Check Instagram Direct messages."""
        self._log("[IG] Checking messages...")
        
        try:
            # Go to Instagram DM
            page_url = "https://www.instagram.com/direct/inbox/"
            
            self.page = self.browser.new_page()
            self.page.goto(page_url, timeout=60000)
            
            # Wait for page to load
            self.page.wait_for_timeout(5000)
            
            # Check if logged in
            if "login" in self.page.url.lower():
                self._log("[IG] Not logged in, attempting login...")
                self.instagram_login()
            
            # Look for message threads
            try:
                # Find message threads
                message_threads = self.page.query_selector_all('div[role="listitem"]')
                
                if message_threads:
                    self._log(f"[IG] Found {len(message_threads)} message threads")
                    
                    # Check first few threads
                    for thread in message_threads[:5]:
                        try:
                            sender_elem = thread.query_selector('span[dir="auto"]')
                            message_elem = thread.query_selector('span[dir="auto"] + span')
                            
                            if sender_elem and message_elem:
                                sender = sender_elem.inner_text()
                                message = message_elem.inner_text()
                                
                                if self.is_new_message(sender, message):
                                    self._log(f"[IG] New message from {sender}: {message[:50]}...")
                                    self._save_to_inbox("instagram", sender, message)
                                    
                        except Exception as e:
                            continue
                else:
                    self._log("[IG] No message threads found")
                    
            except Exception as e:
                self._log(f"[IG] Error checking messages: {e}")
            
            self.page.close()
            self._log("[IG] Check complete")
            
        except Exception as e:
            self._log(f"[IG] Error: {e}")
            self.errors += 1
    
    def facebook_login(self):
        """Login to Facebook."""
        try:
            self.page.goto("https://www.facebook.com/login/", timeout=60000)
            self.page.wait_for_timeout(3000)
            
            # Fill credentials
            self.page.fill('#email', FB_EMAIL)
            self.page.fill('#pass', FB_PASSWORD)
            
            # Click login
            self.page.click('button[type="submit"]')
            
            # Wait for navigation
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(5000)
            
            self._log("[FB] Login attempt complete")
            
        except Exception as e:
            self._log(f"[FB] Login failed: {e}")
            self.errors += 1
    
    def instagram_login(self):
        """Login to Instagram."""
        try:
            self.page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
            self.page.wait_for_timeout(5000)
            
            # Fill credentials
            self.page.fill('input[name="username"]', IG_USERNAME)
            self.page.fill('input[name="password"]', IG_PASSWORD)
            
            # Click login
            self.page.click('button[type="submit"]')
            
            # Wait for navigation
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(5000)
            
            self._log("[IG] Login attempt complete")
            
        except Exception as e:
            self._log(f"[IG] Login failed: {e}")
            self.errors += 1
    
    def is_new_message(self, sender, message):
        """Check if message is new (not seen before)."""
        # Simple implementation: always treat as new
        # Can be enhanced with message tracking
        return True
    
    def watch(self):
        """Main watch loop."""
        self._log("=" * 60)
        self._log("👁️  FB/IG Watcher Started")
        self._log(f"[CONFIG] Check interval: {CHECK_INTERVAL}s")
        self._log(f"[CONFIG] Inbox: {INBOX_DIR}")
        self._log(f"[CONFIG] Session: {SESSION_DIR}")
        self._log("=" * 60)
        
        self.launch_browser()
        
        try:
            while True:
                # Check Facebook
                self.check_facebook_messages()
                
                # Wait a bit
                time.sleep(10)
                
                # Check Instagram
                self.check_instagram_messages()
                
                # Wait until next check
                self._log(f"[WAIT] Next check in {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
                
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
    
    parser = argparse.ArgumentParser(description="FB/IG Message Watcher")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL, help="Check interval in seconds")
    args = parser.parse_args()
    
    CHECK_INTERVAL = args.interval
    
    watcher = FBIGWatcher()
    watcher.watch()
