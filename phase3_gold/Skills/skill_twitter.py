"""
Agent Skill: Twitter/X Poster
Gold Tier - Social Media Integration (Requirement #5)

Usage:
    from skill_twitter import TwitterSkill
    tw = TwitterSkill()
    tw.post("Hello from AI Employee!")
    summary = tw.generate_summary()
"""

import os
import sys
import json
import time
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
    from config import TWITTER_EMAIL, TWITTER_PASSWORD
except ImportError as e:
    print(f"Import error: {e}")


class TwitterSkill:
    """Twitter/X posting skill with error recovery and audit logging."""
    
    def __init__(self):
        self.session_dir = "./twitter_session"
        self.storage_file = os.path.join(self.session_dir, "storage_state.json")
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"
        
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.last_post = None
        self.post_count = 0
        self.errors = []
        
        self._log("TwitterSkill initialized")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(self.log_dir, f"twitter_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details, success=True):
        audit_file = os.path.join(self.log_dir, "twitter_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _take_screenshot(self, page, name):
        try:
            filename = os.path.join(self.screenshot_dir, f"tw_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            page.screenshot(path=filename)
            return filename
        except:
            return None
    
    def _load_session(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return None
    
    def _save_session(self, context):
        try:
            storage = context.storage_state()
            with open(self.storage_file, 'w') as f:
                json.dump(storage, f)
            self._log("Session saved")
        except Exception as e:
            self._log(f"Session save failed: {e}")
    
    def _human_delay(self, min_ms=800, max_ms=2000):
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))
    
    def post(self, text, max_retries=3):
        """
        Post to Twitter/X.
        
        Args:
            text: Tweet text (max 280 characters)
            max_retries: Number of retry attempts
            
        Returns:
            dict: Result with success status
        """
        # Truncate if too long
        if len(text) > 280:
            text = text[:277] + "..."
            self._log("Text truncated to 280 characters")
        
        self._log(f"Starting post: {text[:50]}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                result = self._post_internal(text)
                
                if result["success"]:
                    self.last_post = {
                        "text": text,
                        "timestamp": datetime.now().isoformat(),
                        "platform": "twitter"
                    }
                    self.post_count += 1
                    self._save_audit("post", {"text": text}, True)
                    self._log("Post successful!")
                    return result
                else:
                    self._log(f"Post failed: {result.get('error', 'Unknown')}")
                    self.errors.append(result.get('error', 'Unknown'))
                    self._save_audit("post", {"text": text[:100]}, False)
                    
            except Exception as e:
                self._log(f"Attempt {attempt} error: {e}")
                self.errors.append(str(e))
                
                if attempt < max_retries:
                    self._log(f"Retrying... ({attempt}/{max_retries})")
                    self._human_delay(5000, 10000)
                else:
                    self._save_audit("post", {"text": text[:100], "error": str(e)}, False)
                    return {"success": False, "error": str(e), "attempts": max_retries}
        
        return {"success": False, "error": "All retries failed", "attempts": max_retries}
    
    def _post_internal(self, text):
        playwright = None
        browser = None
        context = None
        page = None
        
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=False,
                    slow_mo=800,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
                )
                
                storage = self._load_session()
                
                context = browser.new_context(
                    storage_state=storage,
                    viewport={"width": 1280, "height": 720}
                )
                
                page = context.new_page()
                
                # Navigate to Twitter
                self._log("Navigating to Twitter/X...")
                page.goto("https://twitter.com", timeout=60000)
                self._human_delay(5000, 8000)
                
                # Check login
                if not self._is_logged_in(page):
                    self._log("Not logged in, attempting login...")
                    if not self._login(page):
                        return {"success": False, "error": "Login failed"}
                
                self._save_session(context)
                
                # Create tweet
                self._log("Creating tweet...")
                if not self._create_tweet(page, text):
                    return {"success": False, "error": "Tweet creation failed"}
                
                return {"success": True, "text": text}
                
        except Exception as e:
            self._log(f"Post error: {e}")
            if page:
                self._take_screenshot(page, "error")
            return {"success": False, "error": str(e)}
        finally:
            try:
                if context: context.close()
                if browser: browser.close()
                if playwright: playwright.stop()
            except:
                pass
    
    def _is_logged_in(self, page):
        try:
            selectors = [
                "[data-testid='tweetButton']",
                "[aria-label='Tweet']",
                "[data-testid='primaryColumn']",
            ]
            for sel in selectors:
                try:
                    if page.is_visible(sel, timeout=5000):
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _login(self, page):
        try:
            self._log("Entering credentials...")
            
            # Username/Email
            try:
                username_input = page.locator("input[type='text'], input[name='text']").first
                username_input.wait_for(state='visible', timeout=10000)
                username_input.fill(TWITTER_EMAIL)
                self._human_delay(1000, 2000)
                
                # Click Next
                next_btn = page.locator("button:has-text('Next')").first
                next_btn.click()
                self._human_delay(3000, 5000)
            except Exception as e:
                self._log(f"Username input failed: {e}")
                return False
            
            # Password
            try:
                password_input = page.locator("input[type='password'], input[name='password']").first
                password_input.wait_for(state='visible', timeout=10000)
                password_input.fill(TWITTER_PASSWORD)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Password input failed: {e}")
                return False
            
            # Login button
            try:
                login_btn = page.locator("button:has-text('Log in'), button:has-text('Log In')").first
                login_btn.click()
                self._human_delay(8000, 12000)
            except:
                page.keyboard.press("Enter")
                self._human_delay(8000, 12000)
            
            self._log("Login completed")
            return True
            
        except Exception as e:
            self._log(f"Login error: {e}")
            self._take_screenshot(page, "login_error")
            return False
    
    def _create_tweet(self, page, text):
        try:
            # Click Tweet button
            self._log("Opening tweet composer...")
            try:
                tweet_btn = page.locator("[data-testid='SideNav_NewTweet'], [aria-label='Tweet']").first
                tweet_btn.click()
                self._human_delay(2000, 3000)
            except Exception as e:
                self._log(f"Tweet button failed: {e}")
                # Try alternative - keyboard shortcut
                page.keyboard.press("Control+n")
                self._human_delay(2000, 3000)
            
            # Type tweet text
            self._log("Typing tweet...")
            try:
                text_area = page.locator("[data-contents='true'], [role='textbox'], [aria-label='Tweet text']").first
                text_area.fill(text)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Text input failed: {e}")
                return False
            
            # Click Post/Tweet button
            self._log("Clicking Post button...")
            try:
                post_btn = page.locator("[data-testid='tweetButton'], button:has-text('Post'), button:has-text('Tweet')").first
                post_btn.click()
                self._human_delay(5000, 8000)
            except Exception as e:
                self._log(f"Post button failed: {e}")
                return False
            
            # Wait for confirmation
            self._human_delay(3000, 5000)
            self._log("Tweet posted!")
            return True
            
        except Exception as e:
            self._log(f"Create tweet error: {e}")
            self._take_screenshot(page, "tweet_error")
            return False
    
    def generate_summary(self):
        return {
            "platform": "Twitter/X",
            "total_posts": self.post_count,
            "last_post": self.last_post,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def get_stats(self):
        return self.generate_summary()


if __name__ == "__main__":
    print("Twitter Skill - Test Mode")
    print("=" * 50)
    
    tw = TwitterSkill()
    result = tw.post("Test from Twitter Skill! #AI #Automation")
    
    print("\nResult:", result)
    print("\nSummary:", tw.generate_summary())
