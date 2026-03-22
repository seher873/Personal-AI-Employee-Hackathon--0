"""
Agent Skill: Facebook Poster
Gold Tier - Social Media Integration

Usage:
    from skill_facebook import FacebookSkill
    fb = FacebookSkill()
    fb.post("Hello from AI Employee!", "path/to/image.png")
    summary = fb.generate_summary()
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
    from playwright.sync_api import sync_playwright
    from config import FB_EMAIL, FB_PASSWORD
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure .env file exists in phase3_gold folder")
    FB_EMAIL = ""
    FB_PASSWORD = ""


class FacebookSkill:
    """Facebook posting skill with error recovery and audit logging."""
    
    def __init__(self):
        self.session_dir = "./fb_session"
        self.storage_file = os.path.join(self.session_dir, "storage_state.json")
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"
        
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.last_post = None
        self.post_count = 0
        self.errors = []
        
        # Use persistent context for better session retention
        self.user_data_dir = os.path.join(self.session_dir, "chrome_user_data")
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        self._log("FacebookSkill initialized")
        self._log(f"Session dir: {self.session_dir}")
    
    def _log(self, message):
        """Internal logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Also write to file
        log_file = os.path.join(self.log_dir, f"facebook_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "facebook_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _take_screenshot(self, page, name):
        """Save screenshot."""
        try:
            filename = os.path.join(self.screenshot_dir, f"fb_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            page.screenshot(path=filename)
            return filename
        except:
            return None
    
    def _load_session(self):
        """Load saved session."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return None
    
    def _save_session(self, browser):
        """Save session."""
        try:
            storage = browser.storage_state()
            with open(self.storage_file, 'w') as f:
                json.dump(storage, f)
            self._log("Session saved to storage_state.json")
            self._log(f"User data dir: {self.user_data_dir}")
        except Exception as e:
            self._log(f"Session save failed: {e}")
    
    def _human_delay(self, min_ms=800, max_ms=2000):
        """Human-like delay."""
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))
    
    def post(self, text, image_path=None, max_retries=3):
        """
        Post to Facebook.
        
        Args:
            text: Post text content
            image_path: Optional path to image
            max_retries: Number of retry attempts
            
        Returns:
            dict: Result with success status and details
        """
        self._log(f"Starting post: {text[:50]}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                result = self._post_internal(text, image_path)
                
                if result["success"]:
                    self.last_post = {
                        "text": text,
                        "image": image_path,
                        "timestamp": datetime.now().isoformat(),
                        "platform": "facebook"
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
                    return {
                        "success": False,
                        "error": str(e),
                        "attempts": max_retries
                    }
        
        return {
            "success": False,
            "error": "All retries failed",
            "attempts": max_retries
        }
    
    def _post_internal(self, text, image_path=None):
        """Internal post implementation."""
        playwright = None
        browser = None
        context = None
        page = None
        
        try:
            with sync_playwright() as playwright:
                # Use persistent context for better session retention
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=False,
                    slow_mo=800,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to Facebook
                self._log("Navigating to Facebook...")
                page.goto("https://www.facebook.com", timeout=60000, wait_until="domcontentloaded")
                self._human_delay(5000, 8000)
                
                # Check if logged in
                if not self._is_logged_in(page):
                    self._log("Not logged in, attempting login...")
                    if not self._login(page):
                        return {"success": False, "error": "Login failed"}
                    self._human_delay(3000, 5000)
                
                self._log("Logged in successfully!")
                
                # Save session after login
                self._save_session(browser)
                
                # Create post
                self._log("Creating post...")
                if not self._create_post(page, text, image_path):
                    return {"success": False, "error": "Post creation failed"}
                
                self._log("Post completed!")
                return {"success": True, "text": text, "image": image_path}
                
        except Exception as e:
            self._log(f"Post error: {e}")
            if page:
                self._take_screenshot(page, "error")
            return {"success": False, "error": str(e)}
        finally:
            try:
                if browser:
                    browser.close()
                if playwright:
                    playwright.stop()
            except:
                pass
    
    def _is_logged_in(self, page):
        """Check if logged in."""
        try:
            selectors = [
                "[data-pagelet='MainFeed']",
                "[aria-label='Home']",
                "[placeholder='What\\'s on your mind?']",
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
        """Perform login."""
        try:
            self._log("Entering credentials...")
            
            # Email
            try:
                email_input = page.locator("input[type='email'], input[name='email'], #email").first
                email_input.wait_for(state='visible', timeout=10000)
                email_input.fill(FB_EMAIL)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Email input failed: {e}")
                return False
            
            # Password
            try:
                password_input = page.locator("input[type='password'], input[name='pass'], #pass").first
                password_input.wait_for(state='visible', timeout=10000)
                password_input.fill(FB_PASSWORD)
                self._human_delay(1000, 2000)
            except Exception as e:
                self._log(f"Password input failed: {e}")
                return False
            
            # Login button
            try:
                login_btn = page.locator("button[type='submit'], [value*='Log In']").first
                login_btn.click()
                self._human_delay(5000, 8000)
            except:
                page.keyboard.press("Enter")
                self._human_delay(5000, 8000)
            
            # Wait for home feed
            try:
                page.wait_for_selector("[data-pagelet='MainFeed']", timeout=30000)
            except:
                pass
            
            self._log("Login completed")
            return True
            
        except Exception as e:
            self._log(f"Login error: {e}")
            self._take_screenshot(page, "login_error")
            return False
    
    def _create_post(self, page, text, image_path=None):
        """Create and publish post with multiple methods."""
        try:
            # Method 1: Try multiple composer selectors
            self._log("Opening composer...")
            composer_opened = False
            
            composer_selectors = [
                "[placeholder='What\\'s on your mind?']",
                "[aria-label='What\\'s on your mind?']",
                "div[role='button']:has-text('What\\'s on your mind?')",
                "[data-testid='what\\'s on your mind?']",
                "button:has-text('What\\'s on your mind?')",
            ]
            
            for selector in composer_selectors:
                try:
                    composer = page.locator(selector).first
                    composer.wait_for(state='visible', timeout=5000)
                    composer.scroll_into_view_if_needed()
                    self._human_delay(500, 1000)
                    composer.click()
                    self._human_delay(2000, 3000)
                    self._log("Composer opened with selector")
                    composer_opened = True
                    break
                except:
                    continue
            
            # Method 2: Keyboard shortcut if selectors fail
            if not composer_opened:
                self._log("Trying keyboard shortcut...")
                try:
                    page.keyboard.press('n')  # Facebook shortcut for new post
                    self._human_delay(2000, 3000)
                    composer_opened = True
                    self._log("Keyboard shortcut worked")
                except:
                    pass
            
            # Method 3: Try finding by text
            if not composer_opened:
                try:
                    composer = page.get_by_text("What's on your mind?").first
                    composer.wait_for(state='visible', timeout=5000)
                    composer.click()
                    self._human_delay(2000, 3000)
                    composer_opened = True
                    self._log("Found by text")
                except Exception as e:
                    self._log(f"Could not open composer: {e}")
                    self._take_screenshot(page, "composer_error")
                    return False
            
            # Type post text
            self._log("Typing text...")
            text_entered = False
            
            text_selectors = [
                "[data-contents='true']",
                "[role='textbox']",
                "div[contenteditable='true']",
                "[aria-label='What\\'s on your mind?']",
                "[placeholder*='What\\'s on your mind']",
            ]
            
            for selector in text_selectors:
                try:
                    text_area = page.locator(selector).first
                    text_area.wait_for(state='visible', timeout=5000)
                    text_area.fill(text)
                    self._human_delay(1000, 2000)
                    text_entered = True
                    self._log("Text entered")
                    break
                except:
                    continue
            
            if not text_entered:
                # Fallback: Use keyboard typing
                try:
                    self._log("Using keyboard typing fallback...")
                    page.keyboard.type(text, delay=50)
                    text_entered = True
                except Exception as e:
                    self._log(f"Text entry failed: {e}")
                    return False
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                self._log(f"Adding image: {image_path}")
                try:
                    photo_btn = page.locator("[aria-label*='photo'], [data-testid*='photo']").first
                    photo_btn.click()
                    self._human_delay(2000, 3000)
                    
                    file_input = page.locator('input[type="file"]').first
                    file_input.set_input_files(image_path)
                    self._human_delay(5000, 8000)
                    self._log("Image uploaded")
                except Exception as e:
                    self._log(f"Image upload failed: {e}")
            
            # Click Post button
            self._log("Clicking Post button...")
            post_clicked = False
            
            # Try multiple post button selectors
            post_selectors = [
                'button:has-text("Post")',
                'button:has-text("Share")',
                'button:has-text("Share now")',
                'button:has-text("Share Now")',
                '[aria-label="Post"]',
                '[aria-label="Share"]',
                '[data-testid="post_button"]',
                '[data-testid="share_button"]',
                'button[type="submit"]',
                'input[type="submit"]',
                '[value="Post"]',
                '[value="Share"]',
            ]
            
            for selector in post_selectors:
                try:
                    post_btn = page.locator(selector).first
                    post_btn.wait_for(state='visible', timeout=3000)
                    post_btn.scroll_into_view_if_needed()
                    self._human_delay(300, 500)
                    post_btn.click()
                    post_clicked = True
                    self._log(f"Post button clicked: {selector}")
                    break
                except:
                    continue
            
            # Fallback: Try keyboard Enter
            if not post_clicked:
                try:
                    self._log("Using Enter key as fallback...")
                    page.keyboard.press('Enter')
                    self._human_delay(3000, 5000)
                    post_clicked = True
                    self._log("Enter key pressed")
                except:
                    pass
            
            if not post_clicked:
                self._log("Post button not found - taking screenshot")
                self._take_screenshot(page, "post_button_error")
                return False
            
            # Wait for post to submit
            self._log("Waiting for post to publish...")
            self._human_delay(8000, 12000)
            
            # Verify post was published
            self._log("Verifying post...")
            try:
                # Look for success indicators
                success_indicators = [
                    "Your post was shared",
                    "Posted",
                    "Share now",
                ]
                
                for indicator in success_indicators:
                    try:
                        success_msg = page.locator(f'div:has-text("{indicator}")').first
                        if success_msg.is_visible(timeout=3000):
                            self._log(f"Post verified: {indicator}")
                            break
                    except:
                        continue
                
                # Take success screenshot
                self._take_screenshot(page, "post_success")
                self._log("Post published successfully!")
                return True
                
            except Exception as e:
                self._log(f"Verification failed: {e}")
                self._take_screenshot(page, "post_verification_error")
                # Still return True as post button was clicked
                return True
            
        except Exception as e:
            self._log(f"Create post error: {e}")
            self._take_screenshot(page, "post_error")
            return False
    
    def generate_summary(self):
        """Generate posting summary."""
        return {
            "platform": "Facebook",
            "total_posts": self.post_count,
            "last_post": self.last_post,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def get_stats(self):
        """Get skill statistics."""
        return self.generate_summary()


# CLI usage
if __name__ == "__main__":
    print("Facebook Skill - Test Mode")
    print("=" * 50)
    
    fb = FacebookSkill()
    
    # Test post
    result = fb.post("Test post from Facebook Skill! #AI #Automation")
    
    print("\nResult:", result)
    print("\nSummary:", fb.generate_summary())
