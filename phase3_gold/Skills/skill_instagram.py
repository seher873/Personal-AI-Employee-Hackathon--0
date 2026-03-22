"""
Agent Skill: Instagram Poster
Gold Tier - Social Media Integration

Usage:
    from skill_instagram import InstagramSkill
    ig = InstagramSkill()
    ig.post("Hello from AI!", "path/to/image.png")
    summary = ig.generate_summary()
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
    from config import IG_USERNAME, IG_PASSWORD
except ImportError as e:
    print(f"Import error: {e}")


class InstagramSkill:
    """Instagram posting skill with error recovery and audit logging."""
    
    def __init__(self):
        self.session_dir = "./ig_session"
        self.storage_file = os.path.join(self.session_dir, "storage_state.json")
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"
        
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.last_post = None
        self.post_count = 0
        self.errors = []
        
        self._log("InstagramSkill initialized")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(self.log_dir, f"instagram_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details, success=True):
        audit_file = os.path.join(self.log_dir, "instagram_audit.jsonl")
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
            filename = os.path.join(self.screenshot_dir, f"ig_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
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
    
    def post(self, text, image_path=None, max_retries=3):
        """
        Post to Instagram.
        
        Args:
            text: Caption text
            image_path: Path to image (required for Instagram)
            max_retries: Number of retry attempts
            
        Returns:
            dict: Result with success status
        """
        self._log(f"Starting post: {text[:50]}...")
        
        if not image_path or not os.path.exists(image_path):
            return {"success": False, "error": "Image path required for Instagram"}
        
        for attempt in range(1, max_retries + 1):
            try:
                result = self._post_internal(text, image_path)
                
                if result["success"]:
                    self.last_post = {
                        "text": text,
                        "image": image_path,
                        "timestamp": datetime.now().isoformat(),
                        "platform": "instagram"
                    }
                    self.post_count += 1
                    self._save_audit("post", {"text": text[:100], "image": image_path}, True)
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
    
    def _post_internal(self, text, image_path):
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
                
                # Navigate to Instagram
                self._log("Navigating to Instagram...")
                page.goto("https://www.instagram.com/", timeout=60000)
                self._human_delay(5000, 8000)
                
                # Check login
                if not self._is_logged_in(page):
                    self._log("Not logged in, attempting login...")
                    if not self._login(page):
                        return {"success": False, "error": "Login failed"}
                
                self._save_session(context)
                
                # Create post
                self._log("Creating post...")
                if not self._create_post(page, text, image_path):
                    return {"success": False, "error": "Post creation failed"}
                
                return {"success": True, "text": text, "image": image_path}
                
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
                "article[role='article']",
                "[aria-label='Feed']",
                "[role='feed']",
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
            
            # Username
            try:
                username_input = page.locator("input[autocomplete='username'], input[name='username']").first
                username_input.wait_for(state='visible', timeout=10000)
                username_input.fill(IG_USERNAME)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Username input failed: {e}")
                return False
            
            # Password
            try:
                password_input = page.locator("input[type='password'], input[name='password']").first
                password_input.wait_for(state='visible', timeout=10000)
                password_input.fill(IG_PASSWORD)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Password input failed: {e}")
                return False
            
            # Login button
            try:
                login_btn = page.locator("button[type='submit'], button:has-text('Log in')").first
                login_btn.click()
                self._human_delay(8000, 12000)
            except:
                page.keyboard.press("Enter")
                self._human_delay(8000, 12000)
            
            # Handle "Save login" popup
            try:
                save_btn = page.locator("button:has-text('Save'), button:has-text('Not Now')").first
                if save_btn.is_visible(timeout=3000):
                    save_btn.click()
                    self._human_delay(1000, 2000)
            except:
                pass
            
            # Handle notifications popup
            try:
                notif_btn = page.locator("button:has-text('Not Now'), button:has-text('Allow')").first
                if notif_btn.is_visible(timeout=3000):
                    notif_btn.click()
                    self._human_delay(1000, 2000)
            except:
                pass
            
            self._log("Login completed")
            return True
            
        except Exception as e:
            self._log(f"Login error: {e}")
            self._take_screenshot(page, "login_error")
            return False
    
    def _create_post(self, page, text, image_path):
        try:
            # Click Create button
            self._log("Clicking Create button...")
            try:
                create_btn = page.locator("[aria-label='New post'], [aria-label='Create'], div[role='button']:has-text('New')").first
                create_btn.click()
                self._human_delay(3000, 5000)
            except Exception as e:
                self._log(f"Create button failed: {e}")
                self._take_screenshot(page, "create_button_error")
                return False
            
            # Upload image
            self._log(f"Uploading image: {image_path}")
            try:
                self._human_delay(2000, 3000)
                file_input = page.locator('input[type="file"]').first
                file_input.wait_for(state='attached', timeout=10000)
                file_input.set_input_files(image_path)
                self._human_delay(5000, 8000)
            except Exception as e:
                self._log(f"Image upload failed: {e}")
                self._take_screenshot(page, "upload_error")
                return False
            
            # Click Next (crop)
            self._log("Clicking Next (crop)...")
            try:
                next_btn = page.locator('button:has-text("Next"), div[role="button"]:has-text("Next")').first
                next_btn.click()
                self._human_delay(3000, 5000)
            except Exception as e:
                self._log(f"Next button failed: {e}")
                return False
            
            # Click Next (filters) - if visible
            try:
                next_btn2 = page.locator('button:has-text("Next")').first
                if next_btn2.is_visible(timeout=3000):
                    next_btn2.click()
                    self._human_delay(2000, 3000)
            except:
                pass
            
            # Type caption
            if text:
                self._log("Typing caption...")
                try:
                    caption_box = page.locator("[aria-label='Write a caption...'], [placeholder='Write a caption...'], textarea").first
                    caption_box.fill(text)
                    self._human_delay(1000, 2000)
                except Exception as e:
                    self._log(f"Caption failed: {e}")
            
            # Click Share
            self._log("Clicking Share...")
            try:
                share_btn = page.locator('button:has-text("Share"), div[role="button"]:has-text("Share")').first
                share_btn.click()
                self._human_delay(8000, 12000)
            except Exception as e:
                self._log(f"Share button failed: {e}")
                return False
            
            self._log("Post published!")
            return True
            
        except Exception as e:
            self._log(f"Create post error: {e}")
            self._take_screenshot(page, "post_error")
            return False
    
    def generate_summary(self):
        return {
            "platform": "Instagram",
            "total_posts": self.post_count,
            "last_post": self.last_post,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def get_stats(self):
        return self.generate_summary()


if __name__ == "__main__":
    print("Instagram Skill - Test Mode")
    print("=" * 50)
    
    ig = InstagramSkill()
    result = ig.post("Test from Instagram Skill! #AI", "post_image.png")
    
    print("\nResult:", result)
    print("\nSummary:", ig.generate_summary())
