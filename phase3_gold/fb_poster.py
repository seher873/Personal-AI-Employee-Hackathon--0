"""
Facebook Auto Poster - With Dynamic Selectors
Selectors loaded from selectors.json - no code changes needed when website updates.
Run with: python fb_poster.py
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
from config import FB_EMAIL, FB_PASSWORD

# =============================================================================
# CONFIGURATION - Loaded from .env via config.py
# =============================================================================
POST_TEXT = "Hello from AI Employee! 🤖 #AI #Automation"
IMAGE_PATH = None  # CHANGE: Path to image if posting with image
# =============================================================================

SESSION_DIR = "./fb_session"
STORAGE_FILE = os.path.join(SESSION_DIR, "storage_state.json")


def human_delay(min_ms=None, max_ms=None):
    delay = random.uniform(
        (min_ms or get_delay("human_min")) / 1000,
        (max_ms or get_delay("human_max")) / 1000
    )
    time.sleep(delay)


def take_screenshot(page, name):
    try:
        fn = f"error_{name}.png"
        page.screenshot(path=fn)
        print(f"Screenshot: {fn}")
    except:
        pass


def save_session(context, path):
    try:
        s = context.storage_state()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(s, f)
        print("Session saved")
    except Exception as e:
        print(f"Save failed: {e}")


def load_session(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def find_button(page, text_patterns):
    """Find button by text patterns from selectors.json."""
    for pattern in text_patterns:
        try:
            btn = page.locator(f'button:has-text("{pattern}")').first
            if btn.is_visible(timeout=get_timeout("button_wait")):
                return btn
        except:
            pass
    # Fallback: search all buttons
    for btn in page.locator('button').all():
        try:
            txt = btn.text_content(timeout=1000).strip().lower()
            for pattern in text_patterns:
                if pattern.lower() in txt:
                    return btn
        except:
            continue
    return None


def login(page):
    print("Going to Facebook...")
    page.goto("https://www.facebook.com", timeout=get_timeout("page_load"))
    human_delay(5000, 8000)

    # Check if logged in with multiple selectors (more strict)
    login_indicators = [
        "div[aria-label='What's on your mind?']",  # Composer box - only visible when logged in
        "[href='/watch']",  # Watch link in sidebar
        "[href='/marketplace/']",  # Marketplace link
        "[href='/groups/']",  # Groups link
        "div[data-pagelet='MainFeed']",  # Main feed
        "div#ssrb_feed_start",  # Feed start
        "[data-testid='bluebar']",  # Blue bar
    ]
    
    # Also check for login page indicators (to avoid false positives)
    login_page_indicators = [
        "input[type='email']",  # Email field on login page
        "input[type='password']",  # Password field on login page
        "button[value='1']",  # Login button on login page
        "text=Forgotten password?",  # Forgot password link
        "text=Create new account"  # Create account button
    ]
    
    print("Checking if already logged in...")
    
    # First check if we're on login page
    for selector in login_page_indicators:
        try:
            if page.is_visible(selector, timeout=2000):
                print("Login page detected - need to login")
                break
        except:
            continue
    else:
        # If no login page indicators, check for logged in indicators
        for selector in login_indicators:
            try:
                if page.is_visible(selector, timeout=2000):
                    print(f"Already logged in! Found: {selector}")
                    return True
            except:
                continue
    
    # If we reach here, we need to login
    print("Login required - entering credentials...")
    
    # Take screenshot to see current page state
    try:
        page.screenshot(path="error_login_page_state.png")
        print("Current page state saved to: error_login_page_state.png")
    except:
        pass
    
    # Find and fill email
    print("Entering email...")
    selector = get_selector("facebook", "email_field")
    email = page.locator(selector).first
    try:
        email.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        email.fill(FB_EMAIL)
        human_delay(500, 1000)
    except Exception as e:
        print(f"Error entering email: {e}")
        print("Tip: Facebook might be showing a checkpoint or different login flow")
        print("Try logging in manually via browser first, then run this script again")
        take_screenshot(page, "email_input")
        raise

    # Find and fill password
    print("Entering password...")
    selector = get_selector("facebook", "password_field")
    pwd = page.locator(selector).first
    try:
        pwd.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        pwd.fill(FB_PASSWORD)
        human_delay(500, 1000)
    except Exception as e:
        print(f"Error entering password: {e}")
        take_screenshot(page, "password_input")
        raise

    # Click login button
    print("Logging in...")
    login_patterns = get_selector_list("facebook", "login_button")
    login_btn = find_button(page, login_patterns)
    if login_btn:
        login_btn.click()
    else:
        page.keyboard.press("Enter")

    human_delay(get_delay("after_login"), get_delay("after_login") + 3000)

    # Wait for feed - try multiple selectors
    print("Waiting for feed...")
    feed_selectors = [
        "[aria-label='Home']",
        "[data-testid='bluebar']",
        "div#ssrb_feed_start",
        "div[role='feed']",
        "#feed",
        ".mbs._3tm",
        "div[data-pagelet='MainFeed']",
        "[data-nos='true']",
        "div.x1n2onr6"
    ]
    
    login_success = False
    for selector in feed_selectors:
        try:
            page.wait_for_selector(selector, timeout=10000)
            print(f"Login success! Found: {selector}")
            login_success = True
            break
        except:
            continue
    
    if not login_success:
        # Check if we're on a checkpoint/restricted page
        try:
            if page.is_visible("div[data-testid='checkpoint-flow']", timeout=5000):
                take_screenshot(page, "checkpoint_detected")
                raise Exception("Facebook checkpoint detected - manual verification required")
        except:
            pass
        
        take_screenshot(page, "login_failed")
        raise Exception("Login failed - check credentials or Facebook UI changed")
    
    return True


def post(page, text, image=None):
    print("Opening composer...")

    # Click composer
    selector = get_selector("facebook", "composer")
    composer = page.locator(selector).first
    try:
        composer.wait_for(state='visible', timeout=get_timeout("selector_wait"))
        composer.click()
    except:
        # Try finding any post button
        for b in page.locator('button').all():
            txt = b.text_content().lower()
            if 'post' in txt or 'status' in txt:
                b.click()
                break
    human_delay(2000, 3000)

    # Type text
    print("Typing...")
    # Type slowly to avoid triggering hashtag dropdown
    page.keyboard.type(text, delay=100)
    human_delay(2000, 3000)

    # Close any open dropdowns (hashtags, emoji, etc.) by pressing Escape multiple times
    print("Closing any open dropdowns...")
    for _ in range(3):
        page.keyboard.press("Escape")
        human_delay(300, 500)
    
    # Click outside the composer to close any remaining dropdowns, then click back
    try:
        page.mouse.click(100, 100)
        human_delay(500, 1000)
        # Click back in composer area
        composer = page.locator("[aria-label='What\\'s on your mind?'], [placeholder='What\\'s on your mind?']").first
        if composer.is_visible(timeout=5000):
            composer.click()
            human_delay(500, 1000)
    except Exception as e:
        print(f"Error refocusing composer: {e}")

    # Add image
    if image and os.path.exists(image):
        print(f"Adding image: {image}")
        selector = get_selector("facebook", "photo_button")
        photo_btn = page.locator(selector).first
        try:
            photo_btn.wait_for(state='visible', timeout=get_timeout("selector_wait"))
            photo_btn.click()
            human_delay(1000, 2000)
            file_input = page.locator(get_selector("facebook", "file_input")).first
            file_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
            file_input.set_input_files(image)
            human_delay(3000, 5000)
            print("Image added")
        except Exception as e:
            print(f"Error adding image: {e}")

    # Close any open menus/dropdowns before posting
    print("Ensuring all dropdowns are closed...")
    for _ in range(3):
        page.keyboard.press("Escape")
        human_delay(300, 500)
    
    # Click back arrow if "Add to your post" menu is open
    try:
        back_arrow = page.locator("button[aria-label='Back'], button svg[viewBox='0 0 28 28']").first
        if back_arrow.is_visible(timeout=2000):
            back_arrow.click()
            human_delay(500, 1000)
            print("Closed 'Add to your post' menu")
    except:
        pass
    
    # Wait for composer to stabilize
    human_delay(2000, 3000)

    # Click Post button - the blue button at bottom of composer dialog
    print("Posting...")
    try:
        # Facebook's Post button is a blue button at the bottom of the dialog
        # Try multiple selectors to find it
        post_btn = None
        
        # Method 1: Look for button with "Post" text in the dialog
        try:
            post_btn = page.locator("div[role='dialog'] button:has-text('Post')").first
            if not post_btn.is_visible(timeout=5000):
                post_btn = None
        except:
            pass
        
        # Method 2: Look for blue Post button by class
        if post_btn is None:
            try:
                post_btn = page.locator("button.x1n2onr6.x1qjc9v5:has-text('Post')").first
                if not post_btn.is_visible(timeout=5000):
                    post_btn = None
            except:
                pass
        
        # Method 3: Find any button containing "Post" in the composer
        if post_btn is None:
            buttons = page.locator("div[role='dialog'] button").all()
            for btn in buttons:
                try:
                    txt = btn.text_content(timeout=1000).strip()
                    if txt == 'Post':
                        post_btn = btn
                        break
                except:
                    continue
        
        if post_btn and post_btn.is_visible(timeout=5000):
            # Check if button is enabled
            try:
                is_disabled = post_btn.is_disabled(timeout=1000)
                if is_disabled:
                    print("Post button disabled, waiting...")
                    post_btn.wait_for(state='enabled', timeout=10000)
            except:
                pass
            
            # Click the Post button
            post_btn.click(force=True)
            print("Post button clicked!")
            
            # Wait for composer to close
            print("Waiting for post to submit...")
            try:
                page.locator("div[role='dialog']").first.wait_for(state='hidden', timeout=30000)
                print("Composer closed - post submitted!")
            except:
                print("Composer may still be open...")
        else:
            print("Post button not found")
            take_screenshot(page, "post_button_not_found")
    except Exception as e:
        print(f"Error clicking Post: {e}")
        take_screenshot(page, "post_button_error")

    human_delay(5000, 8000)
    print("Posted!")
    
    # Wait for post to appear
    print("Waiting for post to appear on timeline...")
    human_delay(5000, 8000)
    
    # Scroll down to see if post appears
    try:
        page.evaluate("window.scrollBy(0, 500)")
        human_delay(2000, 3000)
    except:
        pass
    
    # Take success screenshot
    try:
        page.screenshot(path="success_post.png")
        print("Screenshot saved: success_post.png")
    except Exception as e:
        print(f"Could not take success screenshot: {e}")
    
    # Verify post was created
    print("Verifying post...")
    human_delay(2000, 3000)
    try:
        # Look for recent post indicators
        recent_post_selectors = [
            "div[data-pagelet='main_feed'] div[role='article']",
            "div[role='article']",
            ".mbs._3tm",
            "div.x1n2onr6 div[role='article']"
        ]
        for selector in recent_post_selectors:
            try:
                posts = page.locator(selector).all()
                if len(posts) > 0:
                    print(f"Found {len(posts)} posts on your timeline")
                    break
            except:
                continue
    except Exception as e:
        print(f"Verification error: {e}")


def main():
    print("=" * 50)
    print("Facebook Auto Poster - Dynamic Selectors")
    print("=" * 50)

    # Validate selectors on startup
    validation = validate_selectors()
    if not validation["valid"]:
        print(f"⚠️ Selector validation issues: {validation['issues']}")
    else:
        print("✅ Selectors loaded successfully")

    os.makedirs(SESSION_DIR, exist_ok=True)
    storage = load_session(STORAGE_FILE)

    if storage:
        print("Using saved session")
    else:
        print("First run - will login")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Always use visible browser for reliability
                slow_mo=600,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                storage_state=storage,
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            login(page)
            save_session(context, STORAGE_FILE)
            post(page, POST_TEXT, IMAGE_PATH)

            print("=" * 50)
            print("SUCCESS!")
            print("=" * 50)

            context.close()
            browser.close()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
