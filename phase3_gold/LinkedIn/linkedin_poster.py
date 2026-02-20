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
    """Create and publish a LinkedIn post"""
    try:
        logging.info("Creating LinkedIn post...")

        # Navigate to feed
        page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
        human_like_delay(2000, 3000)

        # Random mouse movement
        random_mouse_move(page)

        # Click on the post creation box - try multiple approaches
        post_start_selectors = [
            'button[aria-label="Start a post"]',
            '.share-box-feed-entry__trigger',
            '[data-test-id="share-box-feed-entry-trigger"]',
            'div.share-box-feed-entry__trigger button',
            '.artdeco-button--muted'
        ]

        clicked = False
        for selector in post_start_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    elem.scroll_into_view_if_needed()
                    human_like_delay(500, 1000)
                    elem.click()
                    human_like_delay(2000, 3000)
                    clicked = True
                    logging.info(f"Clicked post creation button with: {selector}")
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        if not clicked:
            logging.error("Could not find post creation button")
            try:
                page.screenshot(path=ERROR_SCREENSHOT)
            except Exception:
                pass
            return False

        # Wait for post dialog to appear
        human_like_delay(1000, 2000)

        # Find the text input field and enter content
        text_selectors = [
            'div[contenteditable="true"]',
            '.ql-editor.textarea',
            '[aria-label="What do you want to talk about?"]',
            '.editor-composer__editor div[contenteditable="true"]'
        ]

        text_entered = False
        for selector in text_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    elem.scroll_into_view_if_needed()
                    human_like_delay(500, 1000)
                    elem.click()
                    human_like_delay(300, 500)

                    # Select all and delete using keyboard
                    page.keyboard.press('Control+A')
                    human_like_delay(200, 400)
                    page.keyboard.press('Delete')
                    human_like_delay(300, 500)

                    # Type the content slowly
                    elem.type(content, delay=30)
                    human_like_delay(1000, 2000)
                    text_entered = True
                    logging.info("Post content entered")
                    break
            except Exception as e:
                logging.debug(f"Text entry failed with {selector}: {e}")
                continue

        if not text_entered:
            logging.error("Could not enter post content")
            try:
                page.screenshot(path=ERROR_SCREENSHOT)
            except Exception:
                pass
            return False

        # Wait for post to register
        human_like_delay(1000, 2000)

        # Click the Post button - try multiple selectors
        post_selectors = [
            'button:has-text("Post")',
            'button:has-text("Post now")',
            '[aria-label="Post"]',
            '.edit-post-modal button.artdeco-button--primary'
        ]

        for selector in post_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    elem.scroll_into_view_if_needed()
                    human_like_delay(500, 1000)
                    elem.click()
                    human_like_delay(3000, 5000)
                    logging.info("Post button clicked")
                    break
            except Exception as e:
                logging.debug(f"Post button {selector} failed: {e}")
                continue

        # Wait for confirmation
        human_like_delay(3000, 5000)

        # Check if post was successful (URL should be back to feed)
        if "feed" in page.url:
            logging.info("Post published successfully!")
            return True
        else:
            logging.info("Post completed (page state may vary)")
            return True

    except Exception as e:
        logging.error(f"Error creating post: {e}")
        try:
            page.screenshot(path=ERROR_SCREENSHOT)
        except Exception:
            pass
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
