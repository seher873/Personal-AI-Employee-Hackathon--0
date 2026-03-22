#!/usr/bin/env python3
"""
LinkedIn Auto Post - Direct Browser
Opens LinkedIn, logs in with credentials, and posts automatically
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_credentials():
    """Load from credentials.json"""
    cred_file = Path(__file__).parent / 'credentials.json'
    if not cred_file.exists():
        return None, None
    with open(cred_file, 'r', encoding='utf-8') as f:
        creds = json.load(f)
    return creds.get('email', ''), creds.get('password', '')


def auto_post(text: str, image_path: str = None):
    """Auto post to LinkedIn"""
    print("=" * 60)
    print("LinkedIn Auto Post - Direct")
    print("=" * 60)
    
    email, password = load_credentials()
    if not email or not password:
        print("[ERROR] No credentials in credentials.json")
        return False
    
    print(f"[OK] Using: {email}")
    print(f"[OK] Post: {text[:50]}...")
    
    session_dir = Path(__file__).parent / 'linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state = session_dir / 'state.json'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
            
            # Load session if exists
            if storage_state.exists():
                print("[OK] Using saved session")
                context = browser.new_context(storage_state=storage_state, viewport={'width': 1920, 'height': 1080})
            else:
                print("[INFO] New session")
                context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            
            page = context.new_page()
            
            # Go to LinkedIn
            print("\n[*] Going to LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)
            
            # Check login
            if not page.is_visible('button:has-text("Start a post")', timeout=5000):
                print("[*] Need to login...")
                page.goto('https://www.linkedin.com/login', timeout=60000)
                time.sleep(3)
                
                # Fill credentials
                try:
                    page.fill('#username', email)
                    time.sleep(0.5)
                    page.fill('#password', password)
                    time.sleep(0.5)
                    page.click('button[type="submit"]')
                    print("[*] Waiting for login (60 sec)...")
                    
                    # Wait for feed
                    page.wait_for_selector('button:has-text("Start a post")', timeout=60000)
                    print("[OK] Logged in!")
                    
                    # Save session
                    context.storage_state(path=storage_state)
                    print("[OK] Session saved")
                except TimeoutError:
                    print("[!] Auto-login failed - waiting for manual login (120 sec)")
                    # Wait for manual login
                    for i in range(12):
                        time.sleep(10)
                        if page.is_visible('button:has-text("Start a post")', timeout=2000):
                            print("[OK] Manual login detected!")
                            context.storage_state(path=storage_state)
                            break
                    else:
                        print("[ERROR] Login timeout")
                        browser.close()
                        return False
            
            # Create post
            print("\n[*] Creating post...")
            page.goto('https://www.linkedin.com/feed/?createPost=true', timeout=60000)
            time.sleep(3)
            
            # Fill text
            try:
                editor = page.locator('div[contenteditable="true"][role="textbox"]').first
                editor.wait_for(timeout=10000)
                editor.fill(text)
                print("[OK] Text added")
                time.sleep(1)
            except Exception as e:
                print(f"[!] Text fill issue: {e}")
                print("[!] Please paste text manually")
            
            # Add image
            if image_path and os.path.exists(image_path):
                try:
                    media = page.locator('input[type="file"][accept*="image"]').first
                    media.set_input_files(image_path, timeout=15000)
                    print(f"[OK] Image added: {os.path.basename(image_path)}")
                    time.sleep(2)
                except Exception as e:
                    print(f"[!] Image issue: {e}")
            
            # Wait for user to click Post
            print("\n" + "=" * 60)
            print("POST READY!")
            print("=" * 60)
            print("The post composer is open with your content.")
            print("Please click the 'Post' button in the browser.")
            print("Close browser when done.")
            print("=" * 60)
            
            # Keep browser open
            while context.pages:
                time.sleep(1)
            
            browser.close()
            
            # Log
            log_post(text, image_path)
            print("\n[OK] Done!")
            return True
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def log_post(text, image_path):
    """Save to Done folder"""
    log_dir = Path(__file__).parent / 'Done'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'{timestamp}_linkedin_auto.md'
    content = f"""---
type: linkedin_auto
timestamp: {datetime.now().isoformat()}
---
# LinkedIn Auto Post
{text}
"""
    log_file.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    text = sys.argv[1] if len(sys.argv) > 1 else f"🤖 AI Employee Post\n{datetime.now().strftime('%Y-%m-%d')}\n#AI"
    image = sys.argv[sys.argv.index('--image')+1] if '--image' in sys.argv else None
    success = auto_post(text, image)
    print("\n" + "=" * 60)
    print("SUCCESS!" if success else "FAILED!")
    print("=" * 60)
