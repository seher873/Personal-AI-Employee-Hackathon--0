"""
Instagram Auto Poster - With Dynamic Selectors
Selectors loaded from selectors.json - no code changes needed when website updates.
Run with: python instagram_auto_poster.py
"""

import os
import time
import random
import json
from playwright.sync_api import sync_playwright
from selector_loader import (
    get_selector, get_selector_list, get_timeout, get_delay,
    validate_selectors
)
from config import IG_USERNAME, IG_PASSWORD, POST_TEXT as CAPTION, IMAGE_PATH

# Credentials loaded from .env via config.py

SESSION_DIR = "./instagram_session"
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
    for btn in page.locator('button, div[role="button"], span[role="button"]').all():
        try:
            txt = btn.text_content(timeout=1000).strip().lower()
            for pattern in text_patterns:
                if pattern.lower() in txt:
                    return btn
        except:
            continue
    return None


def perform_login(page):
    """Perform Instagram login flow using dynamic selectors."""
    print("Navigating to Instagram...")
    page.goto("https://www.instagram.com", timeout=get_timeout("page_load"))
    human_delay(4000, 6000)

    # Check if already logged in
    try:
        selector = get_selector("instagram", "home_feed")
        page.wait_for_selector(selector, timeout=5000)
        print("Already logged in - feed loaded")
        return True
    except:
        pass

    # Wait for login page to load
    human_delay(2000, 3000)
    
    # Enter username
    print("Entering username...")
    try:
        selector = get_selector("instagram", "username_field")
        username_input = page.locator(selector).first
        username_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        username_input.fill(IG_USERNAME)
        human_delay(1000, 2000)
    except Exception as e:
        print(f"Error entering username: {e}")
        take_screenshot(page, "username_input")
        raise

    # Enter password
    print("Entering password...")
    try:
        selector = get_selector("instagram", "password_field")
        password_input = page.locator(selector).first
        password_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        password_input.fill(IG_PASSWORD)
        human_delay(1000, 2000)
    except Exception as e:
        print(f"Error entering password: {e}")
        take_screenshot(page, "password_input")
        raise

    # Click Log in
    print("Clicking Log in button...")
    login_patterns = get_selector_list("instagram", "login_button")
    login_button = find_button(page, login_patterns)
    if not login_button:
        # Fallback: submit via Enter
        page.keyboard.press("Enter")
    else:
        login_button.click()
    human_delay(get_delay("after_login"), get_delay("after_login") + 3000)

    # Handle "Save login info" dialog
    save_patterns = get_selector_list("instagram", "save_login_button")
    save_btn = find_button(page, save_patterns)
    if save_btn:
        save_btn.click()
        human_delay(1000, 2000)
        print("Handled save login dialog")

    # Handle notifications dialog
    notif_patterns = get_selector_list("instagram", "notifications_button")
    notif_btn = find_button(page, notif_patterns)
    if notif_btn:
        notif_btn.click()
        human_delay(1000, 2000)
        print("Handled notifications dialog")

    # Wait for home feed
    print("Waiting for home feed to load...")
    try:
        selector = get_selector("instagram", "home_feed")
        page.wait_for_selector(selector, timeout=get_timeout("feed_wait"))
        print("Home feed loaded successfully")
    except Exception as e:
        print(f"Timeout waiting for home feed: {e}")
        take_screenshot(page, "feed_load")
        raise

    print("Login success")
    return True


def create_new_post(page, image_path, caption):
    """Create and post a new Instagram post using dynamic selectors."""
    print("Looking for Create button...")

    create_patterns = get_selector_list("instagram", "create_button")
    create_button = find_button(page, create_patterns)
    
    if not create_button:
        # Fallback: try common selectors
        try:
            create_button = page.locator('[aria-label="New post"], [aria-label="Create"]').first
            create_button.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        except Exception as e:
            print(f"Error finding Create button: {e}")
            take_screenshot(page, "create_button")
            raise
    
    create_button.click()
    print("Create button clicked")
    human_delay(2000, 3000)

    # Upload image
    print(f"Uploading image: {image_path}")
    try:
        file_input = page.locator(get_selector("instagram", "file_input")).first
        file_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        file_input.set_input_files(image_path)
        human_delay(3000, 5000)
        print("Image uploaded")
    except Exception as e:
        print(f"Error uploading image: {e}")
        take_screenshot(page, "image_upload")
        raise

    human_delay(2000, 3000)

    # Click Next (first time)
    print("Clicking Next...")
    next_patterns = get_selector_list("instagram", "next_button")
    next_button = find_button(page, next_patterns)
    if next_button:
        next_button.click()
        human_delay(2000, 3000)
    else:
        take_screenshot(page, "next_button")
        raise Exception("Next button not found")

    # Second Next for filters (if visible)
    next_button2 = find_button(page, next_patterns)
    if next_button2 and next_button2.is_visible(timeout=3000):
        next_button2.click()
        human_delay(2000, 3000)
        print("Clicked second Next (filters)")

    # Type caption
    print("Typing caption...")
    try:
        selector = get_selector("instagram", "caption_box")
        caption_box = page.locator(selector).first
        caption_box.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        caption_box.fill(caption)
        human_delay(1000, 2000)
        print("Caption typed")
    except Exception as e:
        print(f"Error typing caption: {e}")
        take_screenshot(page, "caption_typing")

    # Click Share
    print("Looking for Share button...")
    share_patterns = get_selector_list("instagram", "share_button")
    share_button = find_button(page, share_patterns)
    if not share_button:
        raise Exception("Share button not found")
    share_button.click()
    print("Share clicked")
    human_delay(5000, 8000)

    print("Waiting for post to complete...")
    human_delay(3000, 5000)

    try:
        success_msg = page.locator('div:has-text("shared"), div:has-text("Posted")')
        if success_msg.is_visible(timeout=5000):
            print("Post confirmation received")
    except:
        pass

    print("Post shared successfully!")
    return True


def main():
    """Main function to run Instagram auto poster."""
    print("=" * 60)
    print("Instagram Auto Poster - Dynamic Selectors")
    print("=" * 60)

    # Validate selectors on startup
    validation = validate_selectors()
    if not validation["valid"]:
        print(f"⚠️ Selector validation issues: {validation['issues']}")
    else:
        print("✅ Selectors loaded successfully")

    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at '{IMAGE_PATH}'")
        print("Please update IMAGE_PATH in the configuration section")
        return

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

            perform_login(page)
            save_session(context, STORAGE_FILE)

            create_new_post(page, IMAGE_PATH, CAPTION)

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
