"""
Twitter (X) Auto Poster - With Dynamic Selectors
Selectors loaded from selectors.json - no code changes needed when website updates.
Run with: python twitter_auto_poster.py
"""

import os
import time
import random
import json
from playwright.sync_api import sync_playwright
from selector_loader import (
    get_selector, get_selector_list, get_timeout, get_delay,
    load_selectors, validate_selectors
)
from config import TWITTER_EMAIL, TWITTER_PASSWORD, POST_TEXT as TWEET_TEXT, IMAGE_PATH

# Credentials loaded from .env via config.py

SESSION_DIR = "./twitter_session"
STORAGE_FILE = os.path.join(SESSION_DIR, "storage_state.json")


def human_delay(min_ms=None, max_ms=None):
    """Add human-like random delay between actions."""
    if min_ms is None:
        min_ms = get_delay("human_min")
    if max_ms is None:
        max_ms = get_delay("human_max")
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    time.sleep(delay)


def take_screenshot(page, step_name):
    """Take screenshot on error."""
    try:
        filename = f"error_{step_name}.png"
        page.screenshot(path=filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Could not take screenshot: {e}")


def save_session(context, storage_file):
    """Save session storage for auto-login."""
    try:
        storage = context.storage_state()
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        with open(storage_file, 'w') as f:
            json.dump(storage, f)
        print("Session saved for auto-login")
    except Exception as e:
        print(f"Could not save session: {e}")


def load_session(storage_file):
    """Load session storage if exists."""
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def find_button(page, text_patterns):
    """Find button by text patterns from selectors.json."""
    for pattern in text_patterns:
        try:
            btn = page.locator(f'button:has-text("{pattern}"), div[role="button"]:has-text("{pattern}")').first
            if btn.is_visible(timeout=get_timeout("button_wait")):
                return btn
        except:
            pass
    # Fallback: search all buttons
    for btn in page.locator('button, div[role="button"]').all():
        try:
            txt = btn.text_content(timeout=1000).strip().lower()
            for pattern in text_patterns:
                if pattern.lower() in txt:
                    return btn
        except:
            continue
    return None


def perform_login(page):
    """Perform Twitter login flow using dynamic selectors."""
    print("Navigating to Twitter login...")
    page.goto("https://twitter.com/login", timeout=get_timeout("page_load"))
    human_delay(3000, 5000)

    # Enter email/username
    print("Entering email/username...")
    try:
        selector = get_selector("twitter", "username_field")
        email_input = page.locator(selector).first
        email_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        email_input.fill(TWITTER_EMAIL)
        human_delay(1000, 2000)
    except Exception as e:
        print(f"Error entering email: {e}")
        take_screenshot(page, "email_input")
        raise

    # Click Next
    print("Clicking Next button...")
    next_patterns = get_selector_list("twitter", "next_button")
    next_button = find_button(page, next_patterns)
    if not next_button:
        raise Exception("Next button not found")
    next_button.click()
    human_delay(3000, 5000)

    # Enter password
    print("Entering password...")
    try:
        selector = get_selector("twitter", "password_field")
        password_input = page.locator(selector).first
        password_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        password_input.fill(TWITTER_PASSWORD)
        human_delay(1000, 2000)
    except Exception as e:
        print(f"Error entering password: {e}")
        take_screenshot(page, "password_input")
        raise

    # Click Log in
    print("Clicking Log in button...")
    login_patterns = get_selector_list("twitter", "login_button")
    login_button = find_button(page, login_patterns)
    if not login_button:
        raise Exception("Log in button not found")
    login_button.click()
    human_delay(get_delay("after_login"), get_delay("after_login") + 3000)

    # Wait for home feed
    print("Waiting for home feed to load...")
    try:
        selector = get_selector("twitter", "home_feed")
        page.wait_for_selector(selector, timeout=get_timeout("feed_wait"))
        print("Home feed loaded successfully")
    except Exception as e:
        print(f"Timeout waiting for home feed: {e}")
        take_screenshot(page, "feed_load")
        raise

    print("Login success")
    return True


def post_tweet(page, text, image_path=None):
    """Post a tweet with optional image using dynamic selectors."""
    print("Looking for tweet box...")

    try:
        selector = get_selector("twitter", "tweet_box")
        tweet_box = page.locator(selector).first
        tweet_box.wait_for(state='visible', timeout=get_timeout("post_wait"))
        tweet_box.click()
        human_delay(500, 1000)
    except Exception as e:
        print(f"Tweet box not found: {e}")
        take_screenshot(page, "tweet_box_not_found")
        raise

    print("Typing tweet text...")
    try:
        tweet_box.fill(text)
        human_delay(1000, 2000)
        print("Text typed")
    except Exception as e:
        print(f"Error typing text: {e}")
        take_screenshot(page, "text_typing")
        raise

    if image_path and os.path.exists(image_path):
        print(f"Adding image: {image_path}")
        try:
            selector = get_selector("twitter", "media_button")
            media_button = page.locator(selector).first
            media_button.click()
            human_delay(1000, 2000)
            file_input = page.locator(get_selector("twitter", "file_input")).first
            file_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
            file_input.set_input_files(image_path)
            human_delay(2000, 3000)
            print("Image uploaded")
        except Exception as e:
            print(f"Error uploading image: {e}")
            take_screenshot(page, "image_upload")

    print("Looking for Post button...")
    post_patterns = get_selector_list("twitter", "post_button")
    tweet_button = find_button(page, post_patterns)
    if not tweet_button:
        raise Exception("Post button not found")
    tweet_button.click()
    human_delay(5000, 8000)

    print("Waiting for tweet to post...")
    human_delay(2000, 3000)
    print("Tweet posted successfully!")
    return True


def main():
    """Main function to run Twitter auto poster."""
    print("=" * 60)
    print("Twitter (X) Auto Poster - Dynamic Selectors")
    print("=" * 60)

    # Validate selectors on startup
    validation = validate_selectors()
    if not validation["valid"]:
        print(f"⚠️ Selector validation issues: {validation['issues']}")
    else:
        print("✅ Selectors loaded successfully")

    os.makedirs(SESSION_DIR, exist_ok=True)
    storage_state = load_session(STORAGE_FILE)

    if storage_state:
        print("Existing session found - attempting auto-login")
    else:
        print("First run - will perform login")

    playwright = None
    browser = None
    context = None
    page = None

    try:
        with sync_playwright() as playwright:
            print("Launching browser...")
            browser = playwright.chromium.launch(
                headless=False,  # Visible browser for login
                slow_mo=600,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
            )

            context = browser.new_context(
                storage_state=storage_state,
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            page = context.new_page()

            print("Checking login status...")
            page.goto("https://twitter.com/home", timeout=get_timeout("page_load"))
            human_delay(3000, 5000)

            # Check if logged in by looking for home feed elements
            try:
                selector = get_selector("twitter", "home_feed")
                page.wait_for_selector(selector, timeout=5000)
                print("Already logged in - home feed loaded")
            except:
                print("Not logged in - performing login...")
                perform_login(page)
                save_session(context, STORAGE_FILE)

            post_tweet(page, TWEET_TEXT, IMAGE_PATH)

            print("=" * 60)
            print("All operations completed successfully!")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user - closing browser gracefully...")
    except Exception as e:
        print(f"\nError occurred: {e}")
        if page:
            take_screenshot(page, "final_error")
        raise
    finally:
        if context:
            context.close()
        if browser:
            browser.close()
        print("Browser closed")


if __name__ == "__main__":
    main()
