#!/usr/bin/env python3
"""
LinkedIn Auto Post - Interactive Browser
Opens browser for you to login, then saves session for auto posting
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def save_session():
    """Open browser for manual login and save session"""
    print("=" * 60)
    print("LinkedIn Session Setup")
    print("=" * 60)
    
    session_dir = Path(__file__).parent / 'linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state = session_dir / 'state.json'
    
    print("\n[1/2] Opening browser for login...")
    print("INSTRUCTIONS:")
    print("  1. Login to LinkedIn in the browser window")
    print("  2. Complete any 2FA or CAPTCHA if shown")
    print("  3. Wait for your feed to load")
    print("  4. Close the browser window")
    print("  5. Session will be saved for future posts")
    print("\nPress Enter to open browser...")
    input()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("\n[*] Opening LinkedIn login page...")
        page.goto('https://www.linkedin.com/login', timeout=60000)
        
        print("[*] Waiting for you to login... (close browser when done)")
        try:
            # Wait indefinitely for user to close browser
            while context.pages:
                time.sleep(1)
                if page.is_visible('button:has-text("Start a post")', timeout=1000):
                    print("\n[OK] Login detected!")
        except:
            pass
        
        # Save session
        context.storage_state(path=storage_state)
        print(f"[OK] Session saved to: {storage_state}")
        browser.close()
    
    print("\n[OK] Session setup complete!")
    print("\nNow you can run auto posts with:")
    print("  py linkedin_browser_post.py \"Your post text\"")


def post_to_linkedin(text: str, image_path: str = None):
    """Post using saved session"""
    print("=" * 60)
    print("LinkedIn Auto Post")
    print("=" * 60)
    
    session_dir = Path(__file__).parent / 'linkedin_session'
    storage_state = session_dir / 'state.json'
    
    if not storage_state.exists():
        print("\n[ERROR] No saved session found!")
        print("Run setup first:")
        print("  py linkedin_interactive.py --setup")
        return {'success': False, 'error': 'No session'}
    
    print(f"[OK] Post text: {text[:50]}...")
    
    try:
        with sync_playwright() as p:
            print("\n[1/4] Launching browser...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=storage_state, viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            print("[2/4] Going to LinkedIn feed...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(3)
            
            if not page.is_visible('button:has-text("Start a post")', timeout=5000):
                print("[ERROR] Not logged in. Run setup again.")
                browser.close()
                return {'success': False, 'error': 'Not logged in'}
            
            print("[OK] Logged in!")
            print("[3/4] Creating post...")
            
            # Click post button
            page.locator('button:has-text("Start a post")').first.click()
            time.sleep(2)
            
            # Fill text
            editor = page.locator('div[contenteditable="true"][role="textbox"]').first
            editor.fill(text)
            time.sleep(1)
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                print(f"[INFO] Uploading image: {image_path}")
                media_input = page.locator('input[type="file"][accept*="image"]').first
                media_input.set_input_files(image_path)
                time.sleep(2)
            
            print("[4/4] Publishing...")
            post_btn = page.locator('button:has-text("Post")').first
            post_btn.click()
            time.sleep(3)
            
            # Verify
            page.wait_for_selector('button:has-text("Start a post")', timeout=10000)
            print("[OK] Post published!")
            
            # Log
            log_post(text, image_path)
            
            browser.close()
            return {'success': True, 'timestamp': datetime.now().isoformat()}
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return {'success': False, 'error': str(e)}


def log_post(text, image_path):
    """Save to Done folder"""
    log_dir = Path(__file__).parent / 'Done'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'{timestamp}_linkedin_post.md'
    
    content = f"""---
type: linkedin_post
timestamp: {datetime.now().isoformat()}
status: published
---

# LinkedIn Post

**Posted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{text}

## Media
{'Image: ' + image_path if image_path else 'None'}

✅ Published
"""
    log_file.write_text(content, encoding='utf-8')


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        save_session()
    else:
        text = sys.argv[1] if len(sys.argv) > 1 else f"🤖 AI Employee Auto Post\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#AI #Automation"
        image_path = None
        if '--image' in sys.argv:
            idx = sys.argv.index('--image')
            if idx + 1 < len(sys.argv):
                image_path = sys.argv[idx + 1]
        
        result = post_to_linkedin(text, image_path)
        print("\n" + "=" * 60)
        print("SUCCESS!" if result.get('success') else f"FAILED: {result.get('error')}")
        print("=" * 60)


if __name__ == '__main__':
    main()
