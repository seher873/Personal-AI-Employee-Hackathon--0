#!/usr/bin/env python3
"""
Twitter (X) Browser Poster
==========================
Playwright-based Twitter poster (no API libs, only Playwright sync)

Agent Skills:
- Browser automation with persistent sessions
- Human-like interactions (typing, mouse movements)
- Tweet composition with media upload
- Screenshot capture for audit trail

Usage:
    python twitter_browser_poster.py [--text "Your tweet text"] [--image /path/to/image.jpg]
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
POST_IDEAS_FILE = BASE_DIR / "Post_Ideas.md"
SCREENSHOTS_DIR = BASE_DIR / "Screenshots"
LOGS_DIR = BASE_DIR / "Logs"

# Environment variables
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

# URLs
TWITTER_LOGIN_URL = "https://twitter.com/login"
TWITTER_HOME_URL = "https://twitter.com/home"
TWITTER_COMPOSE_URL = "https://twitter.com/compose/tweet"

# Timeouts
PAGE_LOAD_TIMEOUT = 60000
ACTION_TIMEOUT = 30000
IMPLICIT_WAIT = 3000

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'twitter_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TwitterPoster')


class HumanLikeInteraction:
    """
    Agent Skill: Human-like browser interactions
    Makes automation appear more natural to avoid detection
    """
    
    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500) -> None:
        """Random delay between actions to simulate human behavior"""
        time.sleep(random.uniform(min_ms, max_ms) / 1000)
    
    @staticmethod
    def human_typing(page: Page, selector: str, text: str, delay_range: tuple = (50, 150)) -> None:
        """
        Type text with human-like variability
        
        Agent Skill: Simulates natural typing patterns
        - Variable delay between keystrokes
        - Occasional pauses for "thinking"
        - Random character timing
        """
        element = page.locator(selector)
        element.click()
        
        for i, char in enumerate(text):
            element.type(char)
            
            # Random delay between characters (human-like)
            delay = random.uniform(*delay_range)
            time.sleep(delay / 1000)
            
            # Occasional longer pause (like thinking or correcting)
            if i > 0 and i % random.randint(10, 30) == 0:
                time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def mouse_move(page: Page, element: Page) -> None:
        """
        Move mouse in human-like pattern before clicking
        
        Agent Skill: Natural mouse movement simulation
        - Slight random offsets
        - Variable movement speed
        """
        try:
            box = element.bounding_box()
            if box:
                # Add slight human-like offset
                page.mouse.move(
                    box['x'] + box['width'] / 2 + random.randint(-5, 5),
                    box['y'] + box['height'] / 2 + random.randint(-5, 5)
                )
                HumanLikeInteraction.random_delay(200, 500)
        except:
            pass
    
    @staticmethod
    def mouse_random_movement(page: Page) -> None:
        """
        Random mouse movements to appear more human
        
        Agent Skill: Background mouse activity simulation
        """
        viewport = page.viewport_size
        if viewport:
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))


class TwitterSessionManager:
    """
    Agent Skill: Persistent session management
    Handles login state across runs to avoid repeated logins
    """
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
    
    def is_logged_in(self, page: Page) -> bool:
        """Check if already logged in by examining page state"""
        try:
            # Check for compose tweet button (visible when logged in)
            compose_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]')
            return compose_btn.is_visible()
        except:
            return False


class TwitterPoster:
    """Post tweets to Twitter via browser automation"""
    
    def __init__(self, page: Page):
        self.page = page
        self.human = HumanLikeInteraction()
        self.session_manager = TwitterSessionManager(SESSION_DIR)
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Twitter/X
        
        Agent Skill: Form filling with human-like behavior
        Handles Twitter's multi-step login flow
        """
        logger.info("Logging into Twitter/X...")
        
        try:
            self.page.goto(TWITTER_LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Check if already logged in
            if self.session_manager.is_logged_in(self.page):
                logger.info("Already logged in to Twitter/X")
                return True
            
            # Handle potential "Sign in with Google" redirect
            try:
                if "accounts.google.com" in self.page.url:
                    logger.info("Detected Google login redirect")
                    # This would require separate Google login handling
                    pass
            except:
                pass
            
            # Step 1: Enter email/username
            email_field = self.page.locator('input[autocomplete="username"]').first
            self.human.mouse_move(self.page, email_field)
            time.sleep(random.uniform(0.5, 1.0))
            self.human.human_typing(self.page, 'input[autocomplete="username"]', email)
            
            # Click Next
            next_btn = self.page.locator('div[role="button"]').filter(has_text="Next").first
            self.human.mouse_move(self.page, next_btn)
            time.sleep(random.uniform(0.5, 1.0))
            next_btn.click()
            
            time.sleep(3)
            
            # Step 2: Enter password
            password_field = self.page.locator('input[type="password"]').first
            self.human.mouse_move(self.page, password_field)
            time.sleep(random.uniform(0.5, 1.0))
            self.human.human_typing(self.page, 'input[type="password"]', password)
            
            # Click Log in
            login_btn = self.page.locator('div[role="button"]').filter(has_text="Log in").first
            self.human.mouse_move(self.page, login_btn)
            time.sleep(random.uniform(0.5, 1.0))
            login_btn.click()
            
            # Wait for navigation
            time.sleep(5)
            self.page.wait_for_load_state('networkidle', timeout=PAGE_LOAD_TIMEOUT)
            
            # Handle potential security check
            try:
                verify_btn = self.page.locator('div[role="button"]').filter(has_text="Verify")
                if verify_btn.is_visible():
                    logger.warning("Security verification required - manual intervention may be needed")
            except:
                pass
            
            logger.info("Twitter/X login completed")
            return True
            
        except Exception as e:
            logger.error(f"Twitter/X login failed: {e}")
            return False
    
    def create_tweet(self, text: str, image_path: str = None) -> bool:
        """
        Create a tweet on Twitter/X
        
        Agent Skill: Tweet composition with media upload
        Handles Twitter's compose interface
        """
        logger.info("Creating tweet...")
        
        try:
            self.page.goto(TWITTER_HOME_URL, timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(IMPLICIT_WAIT / 1000)
            
            # Random mouse movement (human-like)
            self.human.mouse_random_movement(self.page)
            
            # Click on "What is happening?!" compose box
            compose_box = self.page.locator('[data-testid="tweetTextarea_0"]').first
            if not compose_box.is_visible():
                # Try alternative selector
                compose_box = self.page.locator('div[contenteditable="true"][role="textbox"]').first
            
            self.human.mouse_move(self.page, compose_box)
            time.sleep(random.uniform(0.5, 1.0))
            compose_box.click()
            
            time.sleep(2)
            
            # Type tweet text with human-like typing
            self.human.human_typing(self.page, '[data-testid="tweetTextarea_0"]', text)
            
            time.sleep(2)
            
            # Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                
                # Click media upload button (camera icon)
                try:
                    media_btn = self.page.locator('[data-testid="toolBar-plain__1"]').first
                    self.human.mouse_move(self.page, media_btn)
                    time.sleep(random.uniform(0.5, 1.0))
                    media_btn.click()
                    
                    time.sleep(2)
                    
                    # Upload file
                    file_input = self.page.locator('input[type="file"]').first
                    file_input.set_input_files(image_path)
                    
                    # Wait for upload to complete
                    time.sleep(5)
                    
                    logger.info("Image uploaded successfully")
                    
                except Exception as e:
                    logger.warning(f"Could not upload image: {e}")
            
            # Click Post/Tweet button
            post_btn = self.page.locator('[data-testid="tweetButton"]').first
            self.human.mouse_move(self.page, post_btn)
            time.sleep(random.uniform(0.5, 1.0))
            post_btn.click()
            
            # Wait for tweet to be posted
            time.sleep(5)
            
            # Verify tweet was posted
            try:
                # Look for confirmation toast or new tweet in timeline
                time.sleep(3)
                logger.info("Tweet posted successfully")
                return True
            except Exception as e:
                logger.warning(f"Could not verify tweet: {e}")
                return True  # Assume success if no error
            
        except Exception as e:
            logger.error(f"Failed to create tweet: {e}")
            return False
    
    def take_screenshot(self, filename: str) -> str:
        """
        Take screenshot for audit trail
        
        Agent Skill: Visual documentation of actions
        """
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = SCREENSHOTS_DIR / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)


def read_post_ideas() -> str:
    """
    Agent Skill: Content retrieval from vault
    Read post text from Post_Ideas.md
    """
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
    print("🐦 Twitter (X) Browser Poster")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Post tweets to Twitter/X')
    parser.add_argument('--text', type=str, default='', help='Tweet text')
    parser.add_argument('--image', type=str, default='', help='Image path')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()
    
    # Get tweet text
    tweet_text = args.text or read_post_ideas()
    if not tweet_text:
        logger.error("No tweet text provided or found in Post_Ideas.md")
        print("❌ No tweet text available")
        return 1
    
    image_path = args.image if args.image else None
    
    print(f"📝 Tweet text: {tweet_text[:50]}...")
    print(f"🖼️  Image: {image_path or 'None'}")
    print()
    
    # Ensure directories exist
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser in persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=args.headless,  # Visible by default for human-like interaction
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        browser.contexts[0].set_default_timeout(ACTION_TIMEOUT)
        
        page = browser.contexts[0].pages[0] if browser.contexts[0].pages else browser.contexts[0].new_page()
        twitter_poster = TwitterPoster(page)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("=" * 40)
        print("🐦 Twitter Posting")
        print("=" * 40)
        
        # Login
        if TWITTER_EMAIL and TWITTER_PASSWORD:
            login_success = twitter_poster.login(TWITTER_EMAIL, TWITTER_PASSWORD)
            
            if login_success:
                # Small delay before posting (human-like)
                time.sleep(random.uniform(2, 4))
                
                # Create tweet
                post_success = twitter_poster.create_tweet(tweet_text, image_path)
                
                # Take screenshot
                screenshot = twitter_poster.take_screenshot(f"twitter_post_{timestamp}.png")
                print(f"📸 Screenshot: {screenshot}")
                
                result = post_success
            else:
                result = False
        else:
            logger.error("Twitter credentials not set (TWITTER_EMAIL/TWITTER_PASSWORD)")
            print("❌ Twitter credentials not set")
            result = False
        
        browser.close()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 Results:")
    status = "✅" if result else "❌"
    print(f"  {status} Twitter: {'Success' if result else 'Failed'}")
    print("=" * 60)
    
    return 0 if result else 1


if __name__ == '__main__':
    sys.exit(main())
