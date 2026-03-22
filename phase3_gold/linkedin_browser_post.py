#!/usr/bin/env python3
"""
LinkedIn Auto Post - Browser Automation
Posts to LinkedIn using browser (no API permissions needed)
Uses email/password from credentials.json
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError

# Handle Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_credentials():
    """Load credentials from credentials.json"""
    cred_file = Path(__file__).parent / 'credentials.json'

    if not cred_file.exists():
        print("[ERROR] credentials.json not found!")
        print("\nCreate credentials.json with:")
        print('{')
        print('  "email": "your_linkedin_email@example.com",')
        print('  "password": "your_linkedin_password"')
        print('}')
        sys.exit(1)

    with open(cred_file, 'r', encoding='utf-8') as f:
        creds = json.load(f)

    return creds.get('email', ''), creds.get('password', '')


def post_to_linkedin(text: str, image_path: str = None):
    """
    Post to LinkedIn using browser automation
    """
    print("=" * 60)
    print("LinkedIn Auto Post - Browser Automation")
    print("=" * 60)

    # Load credentials
    email, password = load_credentials()

    if not email or not password:
        print("[ERROR] Email or password missing in credentials.json")
        sys.exit(1)

    print(f"[OK] Credentials loaded: {email}")
    print(f"[OK] Post text: {text[:50]}...")
    if image_path:
        print(f"[OK] Image: {image_path}")

    # Session directory
    session_dir = Path(__file__).parent / 'linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state = session_dir / 'state.json'

    try:
        with sync_playwright() as p:
            # Launch browser
            print("\n[1/6] Launching browser...")
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            # Load existing session or create new
            if storage_state.exists():
                print("[INFO] Loading saved session...")
                context = browser.new_context(
                    storage_state=storage_state,
                    viewport={'width': 1920, 'height': 1080}
                )
            else:
                print("[INFO] New session, will login...")
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

            page = context.new_page()

            # Go to LinkedIn
            print("[2/6] Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)

            # Check if logged in
            logged_in = False
            if page.is_visible('button:has-text("Start a post")', timeout=5000):
                print("[OK] Already logged in!")
                logged_in = True
            else:
                print("[3/6] Logging in...")
                page.goto('https://www.linkedin.com/login', timeout=60000)
                time.sleep(3)

                # Fill email
                email_field = page.locator('#username')
                email_field.wait_for(timeout=10000)
                email_field.fill(email)
                time.sleep(random.uniform(0.5, 1.5))

                # Fill password
                password_field = page.locator('#password')
                password_field.fill(password)
                time.sleep(random.uniform(0.5, 1.5))

                # Click sign in
                sign_in_btn = page.locator('button[type="submit"]')
                sign_in_btn.click()

                # Wait for login
                print("[INFO] Waiting for login (up to 60 seconds)...")
                try:
                    page.wait_for_selector('button:has-text("Start a post")', timeout=60000)
                    print("[OK] Login successful!")
                    context.storage_state(path=storage_state)
                    print("[OK] Session saved")
                    logged_in = True
                except TimeoutError:
                    print("[WARN] Auto login timed out. Waiting for manual login...")
                    for i in range(12):
                        time.sleep(10)
                        if page.is_visible('button:has-text("Start a post")', timeout=2000):
                            print("[OK] Manual login detected!")
                            context.storage_state(path=storage_state)
                            logged_in = True
                            break
                    else:
                        print("[ERROR] Login timeout")
                        browser.close()
                        return {'success': False, 'error': 'Login timeout'}

            if not logged_in:
                browser.close()
                return {'success': False, 'error': 'Not logged in'}

            # Create post
            print("[4/6] Creating post...")

            # Click "Start a post"
            try:
                start_post_btn = page.locator('button:has-text("Start a post")').first
                start_post_btn.click(timeout=10000)
                time.sleep(2)
            except:
                page.goto('https://www.linkedin.com/feed/?createPost=true', timeout=60000)
                time.sleep(3)

            # Fill text
            try:
                editor = page.locator('div[contenteditable="true"][role="textbox"]').first
                editor.wait_for(timeout=10000)
                editor.fill(text)
                time.sleep(1)
                print("[OK] Post text added")
            except Exception as e:
                print(f"[ERROR] Could not fill text: {e}")
                browser.close()
                return {'success': False, 'error': 'Could not fill text'}

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                print("[5/6] Uploading image...")
                try:
                    media_btn = page.locator('input[type="file"][accept*="image"]').first
                    media_btn.set_input_files(image_path, timeout=15000)
                    time.sleep(3)
                    print("[OK] Image uploaded")
                except Exception as e:
                    print(f"[WARN] Image upload may have failed: {e}")

            # Click Post button
            print("[6/6] Publishing post...")
            try:
                post_btn = page.locator('button:has-text("Post")').first
                post_btn.wait_for(timeout=10000)
                post_btn.click()
                time.sleep(3)

                page.wait_for_selector('button:has-text("Start a post")', timeout=10000)
                print("[OK] Post published successfully!")

                # Save to audit log
                log_post(text, image_path)

                browser.close()
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'text': text[:100]
                }

            except Exception as e:
                print(f"[ERROR] Post failed: {e}")
                browser.close()
                return {'success': False, 'error': str(e)}

    except Exception as e:
        print(f"[ERROR] Browser error: {e}")
        return {'success': False, 'error': str(e)}


def log_post(text: str, image_path: str = None):
    """Log post to audit file"""
    log_dir = Path(__file__).parent / 'Done'
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'{timestamp}_linkedin_browser_post.md'

    content = f"""---
type: linkedin_browser_post
timestamp: {datetime.now().isoformat()}
status: published
---

# LinkedIn Post (Browser Automation)

**Posted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content

{text}

## Media

{'Image: ' + image_path if image_path else 'No image'}

## Status

✅ Published successfully via Browser Automation
"""

    log_file.write_text(content, encoding='utf-8')
    print(f"[OK] Logged to: {log_file.name}")


def main():
    """Main function"""
    default_text = f"""🤖 AI Employee Auto Post Test

Testing automated LinkedIn posting via Browser Automation.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AI #Automation #LinkedIn"""

    if len(sys.argv) < 2:
        print("Usage:")
        print('  py linkedin_browser_post.py "Your post text"')
        print('  py linkedin_browser_post.py "Text" --image "image.jpg"')
        print(f"\nUsing default text:")
        print(default_text)
        text = default_text
    else:
        text = sys.argv[1]

    image_path = None
    if '--image' in sys.argv:
        idx = sys.argv.index('--image')
        if idx + 1 < len(sys.argv):
            image_path = sys.argv[idx + 1]

    result = post_to_linkedin(text, image_path)

    print("\n" + "=" * 60)
    if result.get('success'):
        print("SUCCESS! Post published to LinkedIn")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
