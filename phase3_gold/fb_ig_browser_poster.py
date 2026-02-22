#!/usr/bin/env python3
"""
Facebook & Instagram Browser Poster
===================================
Playwright-based poster for FB/IG (no API libs, only Playwright sync)

Agent Skills:
- Browser automation with persistent sessions
- Human-like interactions (typing, mouse movements)
- Screenshot capture for audit trail
- Multi-platform posting (FB + IG)

Usage:
    python fb_ig_browser_poster.py [--text "Your post text"] [--image /path/to/image.jpg]
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext # type: ignore

# Configuration
BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "fb_ig_session"
POST_IDEAS_FILE = BASE_DIR / "Post_Ideas.md"
SCREENSHOTS_DIR = BASE_DIR / "Screenshots"
LOGS_DIR = BASE_DIR / "Logs"

# Environment variables
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")

# URLs
FB_LOGIN_URL = "https://www.facebook.com/login"
FB_POST_URL = "https://www.facebook.com"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"
IG_POST_URL = "https://www.instagram.com"

# Timeouts
PAGE_LOAD_TIMEOUT = 60000
ACTION_TIMEOUT = 30000
IMPLICIT_WAIT = 3000  # 3 seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'fb_ig_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FBIGPoster')


class HumanLikeInteraction:
    """
    Agent Skill: Human-like browser interactions
    Makes automation appear more natural
    """
    
    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500) -> None:
        """Random delay between actions"""
        time.sleep(random.uniform(min_ms, max_ms) / 1000)
    
    @staticmethod
    def human_typing(page: Page, selector: str, text: str, delay_range: tuple = (50, 150)) -> None:
        """
        Type text with human-like variability
        
        Agent Skill: Simulates natural typing patterns
        - Variable delay between keystrokes
        - Occasional pauses for "thinking"
        """
        element = page.locator(selector)
        element.click()
        
        for i, char in enumerate(text):
            element.type(char)
            
            # Random delay between characters
            delay = random.uniform(*delay_range)
            time.sleep(delay / 1000)
            
            # Occasional longer pause (like thinking)
            if i > 0 and i % random.randint(10, 30) == 0:
                time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def mouse_move(page: Page, element: Page) -> None:
        """
        Move mouse in human-like pattern before clicking
        
        Agent Skill: Natural mouse movement simulation
        """
        box = element.bounding_box()
        if box:
            # Move to element with slight offset
            page.mouse.move(
                box['x'] + box['width'] / 2 + random.randint(-5, 5),
                box['y'] + box['height'] / 2 + random.randint(-5, 5)
            )
            HumanLikeInteraction.random_delay(200, 500)


class FBIGSessionManager:
    """
    Agent Skill: Persistent session management
    Handles login state across runs
    """
    
    def __init__(self, context: BrowserContext):
        self.context = context
        self.session_dir = SESSION_DIR
    
    def save_session(self, platform: str) -> None:
        """Save session state"""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        # Note: Playwright doesn't have direct session export in sync API
        # We rely on storage state persistence
        logger.info(f"Session saved for {platform}")
    
    def load_session(self, platform: str) -> bool:
        """Load existing session if available"""
        session_path = self.session_dir / f"{platform}_storage_state.json"
        if session_path.exists():
            logger.info(f"Loaded existing session for {platform}")
            return True
        return False


class FacebookPoster:
    """Post to Facebook via browser automation"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeInteraction()
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Facebook
        
        Agent Skill: Form filling with human-like behavior
        """
        logger.info("Logging into Facebook...")
        
        try:
            self.page.goto(FB_LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Check if already logged in
            if "facebook.com" in self.page.url and "login" not in self.page.url:
                logger.info("Already logged in to Facebook")
                return True
            
            # Find and fill email
            email_field = self.page.locator('#email').first
            self.human.mouse_move(self.page, email_field)
            self.human.human_typing(self.page, '#email', email)
            
            # Find and fill password
            password_field = self.page.locator('#pass').first
            self.human.mouse_move(self.page, password_field)
            self.human.human_typing(self.page, '#pass', password)
            
            # Click login button
            login_btn = self.page.locator('button[name="login"]').first
            self.human.mouse_move(self.page, login_btn)
            time.sleep(random.uniform(0.5, 1.0))
            login_btn.click()
            
            # Wait for navigation
            time.sleep(5)
            self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            
            logger.info("Facebook login completed")
            return True
            
        except Exception as e:
            logger.error(f"Facebook login failed: {e}")
            return False
    
    def create_post(self, text: str, image_path: str = None) -> bool: # pyright: ignore[reportArgumentType]
        """
        Create a post on Facebook
        
        Agent Skill: Post creation with media upload
        """
        logger.info("Creating Facebook post...")
        
        try:
            self.page.goto(FB_POST_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Click on "What's on your mind?" box
            post_box = self.page.locator('[aria-label*="What\'s on your mind"]').first
            if not post_box.is_visible():
                post_box = self.page.locator('div[role="button"]').filter(has_text="What's on your mind").first
            
            self.human.mouse_move(self.page, post_box)
            time.sleep(random.uniform(0.5, 1.0))
            post_box.click()
            
            time.sleep(2)
            
            # Type post text
            text_area = self.page.locator('div[contenteditable="true"][data-lexical-editor="true"]').first
            self.human.human_typing(self.page, 'div[contenteditable="true"][data-lexical-editor="true"]', text)
            
            # Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                
                # Click photo/video button
                photo_btn = self.page.locator('div[role="button"]').filter(has_text="Photo/video").first
                self.human.mouse_move(self.page, photo_btn)
                time.sleep(random.uniform(0.5, 1.0))
                photo_btn.click()
                
                time.sleep(2)
                
                # Upload file
                file_input = self.page.locator('input[type="file"]').first
                file_input.set_input_files(image_path)
                
                # Wait for upload
                time.sleep(5)
            
            # Click Post button
            post_btn = self.page.locator('div[role="button"]').filter(has_text="Post").last
            self.human.mouse_move(self.page, post_btn)
            time.sleep(random.uniform(0.5, 1.0))
            post_btn.click()
            
            # Wait for post to be published
            time.sleep(5)
            
            logger.info("Facebook post created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Facebook post: {e}")
            return False
    
    def take_screenshot(self, filename: str) -> str:
        """Take screenshot for audit trail"""
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = SCREENSHOTS_DIR / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


class InstagramPoster:
    """Post to Instagram via browser automation"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeInteraction()
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to Instagram
        
        Agent Skill: Form filling with human-like behavior
        """
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
            
            # Fill username
            username_field = self.page.locator('input[name="username"]').first
            self.human.mouse_move(self.page, username_field)
            self.human.human_typing(self.page, 'input[name="username"]', username)
            
            # Fill password
            password_field = self.page.locator('input[name="password"]').first
            self.human.mouse_move(self.page, password_field)
            self.human.human_typing(self.page, 'input[name="password"]', password)
            
            # Click login button
            login_btn = self.page.locator('button[type="submit"]').first
            self.human.mouse_move(self.page, login_btn)
            time.sleep(random.uniform(0.5, 1.0))
            login_btn.click()
            
            # Wait for navigation
            time.sleep(5)
            self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            
            # Handle "Save login info" dialog
            try:
                not_now_btn = self.page.locator('button').filter(has_text="Not Now").first
                if not_now_btn.is_visible():
                    not_now_btn.click()
                    time.sleep(2)
            except:
                pass
            
            # Handle notifications dialog
            try:
                not_now_btn = self.page.locator('button').filter(has_text="Not Now").nth(1)
                if not_now_btn.is_visible():
                    not_now_btn.click()
                    time.sleep(2)
            except:
                pass
            
            logger.info("Instagram login completed")
            return True
            
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False
    
    def create_post(self, text: str, image_path: str) -> bool:
        """
        Create a post on Instagram
        
        Agent Skill: Post creation with media upload
        Note: Instagram requires an image for posts
        """
        logger.info("Creating Instagram post...")
        
        if not image_path or not Path(image_path).exists():
            logger.error("Instagram post requires an image")
            return False
        
        try:
            self.page.goto(IG_POST_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Click New Post (+) button
            new_post_btn = self.page.locator('div[role="button"]').filter(has_text="New post").first
            if not new_post_btn.is_visible():
                # Alternative: SVG icon button
                new_post_btn = self.page.locator('svg[aria-label="New post"]').locator('..').first
            
            self.human.mouse_move(self.page, new_post_btn)
            time.sleep(random.uniform(0.5, 1.0))
            new_post_btn.click()
            
            time.sleep(2)
            
            # Upload image
            file_input = self.page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            
            # Wait for image to load
            time.sleep(5)
            
            # Click Next
            next_btn = self.page.locator('button').filter(has_text="Next").first
            self.human.mouse_move(self.page, next_btn)
            time.sleep(random.uniform(0.5, 1.0))
            next_btn.click()
            
            time.sleep(3)
            
            # Click Next again (filters)
            try:
                next_btn = self.page.locator('button').filter(has_text="Next").first
                if next_btn.is_visible():
                    next_btn.click()
                    time.sleep(3)
            except:
                pass
            
            # Add caption
            caption_field = self.page.locator('textarea').first
            self.human.human_typing(self.page, 'textarea', text)
            
            time.sleep(2)
            
            # Click Share
            share_btn = self.page.locator('button').filter(has_text="Share").first
            self.human.mouse_move(self.page, share_btn)
            time.sleep(random.uniform(0.5, 1.0))
            share_btn.click()
            
            # Wait for post to be published
            time.sleep(5)
            
            logger.info("Instagram post created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Instagram post: {e}")
            return False
    
    def take_screenshot(self, filename: str) -> str:
        """Take screenshot for audit trail"""
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = SCREENSHOTS_DIR / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


def read_post_ideas() -> str:
    """Read post text from Post_Ideas.md"""
    if not POST_IDEAS_FILE.exists():
        logger.warning(f"Post ideas file not found: {POST_IDEAS_FILE}")
        return ""
    
    with open(POST_IDEAS_FILE, 'r') as f:
        content = f.read()
    
    # Get the first unused post idea
    lines = content.split('\n')
    for line in lines:
        if line.strip() and not line.startswith('#'):
            return line.strip()
    
    return ""


def main():
    """Main entry point"""
    print("=" * 60)
    print("📱 Facebook & Instagram Browser Poster")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, default='', help='Post text')
    parser.add_argument('--image', type=str, default='', help='Image path')
    parser.add_argument('--platform', type=str, choices=['fb', 'ig', 'both'], default='both',
                       help='Platform to post to')
    args = parser.parse_args()
    
    # Get post text
    post_text = args.text or read_post_ideas()
    if not post_text:
        logger.error("No post text provided or found in Post_Ideas.md")
        print("❌ No post text available")
        return 1
    
    image_path = args.image if args.image else None
    
    print(f"📝 Post text: {post_text[:50]}...")
    print(f"🖼️  Image: {image_path or 'None'}")
    print(f"🎯 Platform: {args.platform}")
    print()
    
    # Ensure directories exist
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser in persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=True,  # Headless mode for automated operation
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        browser.contexts[0].set_default_timeout(ACTION_TIMEOUT)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {}
        
        # Facebook posting
        if args.platform in ['fb', 'both']:
            print("\n" + "=" * 40)
            print("📘 Facebook Posting")
            print("=" * 40)
            
            fb_page = browser.new_page()
            fb_poster = FacebookPoster(fb_page)
            
            # Login
            if FB_EMAIL and FB_PASSWORD:
                login_success = fb_poster.login(FB_EMAIL, FB_PASSWORD)
                if login_success:
                    # Create post
                    post_success = fb_poster.create_post(post_text, image_path)
                    results['facebook'] = post_success
                    
                    # Take screenshot
                    screenshot = fb_poster.take_screenshot(f"fb_post_{timestamp}.png")
                    print(f"📸 Screenshot: {screenshot}")
                else:
                    results['facebook'] = False
            else:
                logger.error("Facebook credentials not set (FB_EMAIL/FB_PASSWORD)")
                results['facebook'] = False
            
            fb_page.close()
        
        # Instagram posting
        if args.platform in ['ig', 'both']:
            print("\n" + "=" * 40)
            print("📷 Instagram Posting")
            print("=" * 40)
            
            ig_page = browser.new_page()
            ig_poster = InstagramPoster(ig_page)
            
            # Login
            if IG_USERNAME and IG_PASSWORD:
                login_success = ig_poster.login(IG_USERNAME, IG_PASSWORD)
                if login_success:
                    # Create post (requires image)
                    if image_path:
                        post_success = ig_poster.create_post(post_text, image_path)
                        results['instagram'] = post_success
                        
                        # Take screenshot
                        screenshot = ig_poster.take_screenshot(f"ig_post_{timestamp}.png")
                        print(f"📸 Screenshot: {screenshot}")
                    else:
                        logger.error("Instagram post requires an image")
                        results['instagram'] = False
                else:
                    results['instagram'] = False
            else:
                logger.error("Instagram credentials not set (IG_USERNAME/IG_PASSWORD)")
                results['instagram'] = False
            
            ig_page.close()
        
        browser.close()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 Results:")
    for platform, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {platform.capitalize()}: {'Success' if success else 'Failed'}")
    print("=" * 60)
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
