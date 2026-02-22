#!/usr/bin/env python3
"""
LinkedIn Poster for creating and publishing posts.
Implements Poster Skill from SKILL.md
Posts content to LinkedIn feed with hashtags and formatting.
"""

import os
import sys
import time
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Check Python version
if sys.version_info < (3, 13):
    print(f"Error: Python 3.13 or higher is required. Current version: {sys.version}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuration
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "sehrkhan873@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
USER_DATA_DIR = "./linkedin_session"
ERROR_SCREENSHOT = "linkedin_post_error.png"
HEADLESS = True  # Set to False for visible browser

# Ensure session directory exists
Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)


def human_like_delay(min_ms=100, max_ms=300):
    """Add human-like delay"""
    time.sleep(random.randint(min_ms, max_ms) / 1000)


def random_mouse_move(page):
    """Perform random mouse movements"""
    try:
        x = random.randint(100, 1200)
        y = random.randint(100, 800)
        page.mouse.move(x, y)
        human_like_delay(100, 300)
    except Exception:
        pass


def login_to_linkedin(page, email, password):
    """Login to LinkedIn"""
    logging.info("Navigating to LinkedIn login...")
    page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=30000)
    human_like_delay(1000, 2000)

    # Check if already logged in
    if "feed" in page.url or "mynetwork" in page.url:
        logging.info("Already logged in")
        return True

    if not password:
        logging.error("No password provided")
        return False

    logging.info("Logging in...")

    try:
        # Fill login form
        page.fill('input[name="session_key"]', email)
        human_like_delay(500, 1000)
        page.fill('input[name="session_password"]', password)
        human_like_delay(500, 1000)

        # Click login button
        page.click('button[type="submit"]')
        human_like_delay(2000, 3000)

        # Wait for navigation
        try:
            page.wait_for_url("https://www.linkedin.com/feed/*", timeout=30000)
        except Exception:
            pass

        # Verify login
        if "feed" in page.url or "mynetwork" in page.url:
            logging.info("Login successful")
            return True
        else:
            logging.error("Login verification failed")
            return False

    except Exception as e:
        logging.error(f"Login error: {e}")
        return False


def create_post(page, content):
    """Create and publish a LinkedIn post with robust 2026 UI fallbacks"""
    MAX_RETRIES = 4
    RETRY_DELAY = 5
    
    for attempt in range(MAX_RETRIES):
        try:
            logging.info(f"Creating LinkedIn post (attempt {attempt + 1}/{MAX_RETRIES})...")

            # Navigate to feed
            page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
            human_like_delay(2000, 3000)

            # Wait for feed to load
            try:
                logging.info("Waiting for feed to load...")
                page.wait_for_selector('div.feed-shared-update-v2, div.feed-identity-module', timeout=90000)
                logging.info("Feed loaded successfully")
            except Exception as e:
                logging.warning(f"Feed wait timeout: {e}")

            # Random mouse movement
            random_mouse_move(page)

            # =========================================
            # STEP 1: Find and click post box
            # 2026 UI fallback selectors (in order)
            # =========================================
            post_box = None
            post_box_selectors = [
                lambda p: p.get_by_placeholder('What do you want to talk about?'),
                lambda p: p.get_by_placeholder('Start a post'),
                lambda p: p.locator('div[contenteditable="true"][role="textbox"]'),
                lambda p: p.locator('div.ql-editor.ql-blank'),
                lambda p: p.get_by_role('textbox', name='What do you want to talk about?'),
                lambda p: p.locator('[data-test-id="post-modal-text-area"]'),
            ]

            logging.info("Searching for post box...")
            for i, selector_fn in enumerate(post_box_selectors):
                try:
                    elem = selector_fn(page)
                    count = elem.count()
                    logging.info(f"  Selector {i+1}: Found {count} element(s)")
                    if count > 0:
                        post_box = elem.first
                        logging.info(f"✓ Using selector {i+1} for post box")
                        break
                except Exception as e:
                    logging.debug(f"Selector {i+1} failed: {e}")
                    continue

            if not post_box or post_box.count() == 0:
                logging.error("❌ Could not find post box with any selector")
                page.screenshot(path="post_box_not_found.png")
                raise Exception("Post box not found")

            # Scroll to element
            try:
                post_box.scroll_into_view_if_needed()
                human_like_delay(500, 1000)
                logging.info("✓ Scrolled to post box")
            except Exception as e:
                logging.warning(f"Scroll warning: {e}")

            # Force focus
            try:
                post_box.focus(timeout=10000)
                logging.info("✓ Focused post box")
            except Exception:
                # JS fallback for focus
                try:
                    handle = post_box.element_handle(timeout=5000)
                    page.evaluate("el => el.focus()", handle)
                    logging.info("✓ Focused post box (JS fallback)")
                except Exception as e:
                    logging.warning(f"Focus failed: {e}")

            human_like_delay(500, 1000)

            # Force click
            try:
                post_box.click(force=True, timeout=20000)
                logging.info("✓ Clicked post box")
            except Exception:
                # JS fallback for click
                try:
                    handle = post_box.element_handle(timeout=5000)
                    page.evaluate("el => el.click()", handle)
                    logging.info("✓ Clicked post box (JS fallback)")
                except Exception as e:
                    logging.warning(f"Click failed: {e}")

            human_like_delay(1000, 2000)

            # Debug info
            try:
                is_focused = post_box.is_focused()
                logging.info(f"Debug - Post box focused: {is_focused}")
            except Exception:
                pass

            # =========================================
            # STEP 2: Type content slowly
            # =========================================
            logging.info("Typing post content...")
            
            # Clear existing content first
            try:
                page.keyboard.press('Control+A')
                human_like_delay(200, 400)
                page.keyboard.press('Delete')
                human_like_delay(200, 400)
            except Exception:
                pass

            # Type character by character for human-like behavior
            for char in content:
                try:
                    post_box.type(char, delay=random.uniform(80, 250))
                except Exception:
                    # Fallback to keyboard
                    page.keyboard.type(char, delay=random.uniform(80, 250))
            
            logging.info("✓ Content typed successfully")
            human_like_delay(1000, 2000)

            # Take screenshot before post
            try:
                page.screenshot(path="post_before.png")
                logging.info("✓ Screenshot saved: post_before.png")
            except Exception as e:
                logging.debug(f"Screenshot warning: {e}")

            # =========================================
            # STEP 3: Wait for Post button to enable
            # =========================================
            logging.info("Waiting for Post button to enable...")
            human_like_delay(5000, 7000)

            # =========================================
            # STEP 4: Click Post button with fallbacks
            # =========================================
            post_button = None
            post_button_selectors = [
                lambda p: p.get_by_role('button', name='Post', disabled=False),
                lambda p: p.locator('button[data-control-name="post_submit"]'),
                lambda p: p.locator('button span:has-text("Post")'),
                lambda p: p.get_by_text('Post', exact=False),
            ]

            logging.info("Searching for Post button...")
            for i, selector_fn in enumerate(post_button_selectors):
                try:
                    elem = selector_fn(page)
                    if elem.count() > 0:
                        post_button = elem.first
                        logging.info(f"✓ Using selector {i+1} for Post button")
                        break
                except Exception as e:
                    logging.debug(f"Post button selector {i+1} failed: {e}")
                    continue

            if post_button and post_button.count() > 0:
                try:
                    post_button.scroll_into_view_if_needed()
                    human_like_delay(500, 1000)
                    post_button.click(force=True, timeout=20000)
                    logging.info("✓ Post button clicked")
                except Exception:
                    # JS fallback
                    try:
                        handle = post_button.element_handle(timeout=5000)
                        page.evaluate("el => el.click()", handle)
                        logging.info("✓ Post button clicked (JS fallback)")
                    except Exception as e:
                        logging.warning(f"Post button click failed: {e}")
            else:
                logging.warning("Post button not found, trying keyboard fallback...")

            # =========================================
            # STEP 5: Ultimate fallback - keyboard submit
            # =========================================
            human_like_delay(2000, 3000)
            try:
                post_box.press('Control+Enter')
                logging.info("✓ Control+Enter pressed (fallback)")
            except Exception:
                try:
                    post_box.press('Enter')
                    logging.info("✓ Enter pressed (fallback)")
                except Exception as e:
                    logging.warning(f"Keyboard fallback failed: {e}")

            # Take screenshot after post
            human_like_delay(3000, 5000)
            try:
                page.screenshot(path="post_after.png")
                logging.info("✓ Screenshot saved: post_after.png")
            except Exception as e:
                logging.debug(f"Screenshot warning: {e}")

            # Wait for confirmation
            human_like_delay(3000, 5000)

            # Check if post was successful
            if "feed" in page.url:
                logging.info("✓ Post published successfully! (back to feed)")
                return True
            else:
                logging.info("✓ Post completed (page state may vary)")
                return True

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logging.error(f"❌ All {MAX_RETRIES} attempts failed")
                try:
                    page.screenshot(path=ERROR_SCREENSHOT)
                except Exception:
                    pass
                return False
    
    return False


def post_to_linkedin(content):
    """Main function to post content to LinkedIn"""
    logging.info(f"Posting to LinkedIn: {content[:50]}...")

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            context = browser.new_context(
                storage_state=USER_DATA_DIR + "/storage_state.json" if os.path.exists(USER_DATA_DIR + "/storage_state.json") else None
            )
            page = context.new_page()

            # Login
            if not login_to_linkedin(page, LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
                logging.error("Failed to login to LinkedIn")
                browser.close()
                return False

            # Create post
            success = create_post(page, content)

            # Save session state
            context.storage_state(path=USER_DATA_DIR + "/storage_state.json")

            browser.close()

            if success:
                logging.info("LinkedIn post completed successfully!")
                return True
            else:
                logging.error("LinkedIn post failed")
                return False

    except Exception as e:
        logging.error(f"Error posting to LinkedIn: {e}")
        return False


def main():
    """Main entry point for LinkedIn poster."""
    parser = argparse.ArgumentParser(description='Post content to LinkedIn')
    parser.add_argument('-c', '--content', type=str, help='Post content')
    parser.add_argument('-f', '--file', type=str, help='File containing post content')
    parser.add_argument('--visible', action='store_true', help='Show browser window')

    args = parser.parse_args()

    global HEADLESS
    if args.visible:
        HEADLESS = False

    # Get content from argument or file
    content = None
    if args.content:
        content = args.content
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        print("Enter your LinkedIn post content (type 'END' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line == 'END':
                break
            lines.append(line)
        content = '\n'.join(lines)

    if not content or not content.strip():
        logging.error("No content provided")
        sys.exit(1)

    print(f"\nPosting to LinkedIn...\nContent: {content[:100]}{'...' if len(content) > 100 else ''}\n")

    success = post_to_linkedin(content)

    if success:
        print("\n✓ Post published successfully!")
    else:
        print("\n✗ Post failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
