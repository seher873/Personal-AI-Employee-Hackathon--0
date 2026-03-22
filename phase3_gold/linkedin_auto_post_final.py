#!/usr/bin/env python3
"""
LinkedIn Auto Post - Gold Tier
Posts to LinkedIn using browser automation
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


def load_credentials():
    """Load credentials from credentials.json"""
    cred_file = Path(__file__).parent / 'credentials.json'
    if not cred_file.exists():
        return None, None
    with open(cred_file, 'r', encoding='utf-8') as f:
        creds = json.load(f)
    return creds.get('email', ''), creds.get('password', '')


def auto_post(text: str, image_path: str = None):
    """Auto post to LinkedIn"""
    print("=" * 60)
    print("LinkedIn Auto Post")
    print("=" * 60)
    
    email, password = load_credentials()
    if not email or not password:
        print("[ERROR] No credentials in credentials.json")
        print("Create credentials.json with email and password")
        return False
    
    print(f"[OK] Account: {email}")
    print(f"[OK] Post: {text[:60]}...")
    if image_path:
        print(f"[OK] Image: {image_path}")
    
    session_dir = Path(__file__).parent / 'linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state = session_dir / 'state.json'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            # Load or create session
            if storage_state.exists():
                print("[OK] Loading saved session...")
                context = browser.new_context(storage_state=storage_state)
            else:
                print("[INFO] New session - will login")
                context = browser.new_context()
            
            page = context.new_page()
            
            # Go to LinkedIn
            print("\n[*] Opening LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)
            
            # Check if logged in
            if not page.is_visible('button:has-text("Start a post")', timeout=5000):
                print("[*] Logging in...")
                page.goto('https://www.linkedin.com/login', timeout=60000)
                time.sleep(3)
                
                # Fill credentials
                page.fill('#username', email)
                time.sleep(0.5)
                page.fill('#password', password)
                time.sleep(0.5)
                page.click('button[type="submit"]')
                
                # Wait for login
                print("[*] Waiting for login (90 sec)...")
                try:
                    page.wait_for_selector('button:has-text("Start a post")', timeout=90000)
                    print("[OK] Logged in!")
                    
                    # Save session
                    context.storage_state(path=storage_state)
                    print("[OK] Session saved for next time")
                except:
                    print("[!] Waiting for manual login...")
                    for i in range(12):
                        time.sleep(10)
                        if page.is_visible('button:has-text("Start a post")', timeout=2000):
                            print("[OK] Login detected!")
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
                print(f"[!] Text issue: {e}")
            
            # Add image
            if image_path and os.path.exists(image_path):
                try:
                    media = page.locator('input[type="file"][accept*="image"]').first
                    media.set_input_files(image_path, timeout=15000)
                    print(f"[OK] Image added")
                    time.sleep(2)
                except Exception as e:
                    print(f"[!] Image issue: {e}")
            
            # Click Post button
            print("\n[*] Publishing (wait 5 sec)...")
            try:
                post_btn = page.locator('button:has-text("Post")').first
                post_btn.wait_for(timeout=10000)
                post_btn.click()
                time.sleep(5)
                print("[OK] Post published!")
                
                # Save log
                log_post(text, image_path)
            except:
                print("[!] Please click Post button manually")
                print("[*] Waiting for you to complete...")
                while context.pages:
                    time.sleep(1)
            
            browser.close()
            return True
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def log_post(text, image_path):
    """Save to Done folder"""
    log_dir = Path(__file__).parent / 'Done'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'{timestamp}_linkedin.md'
    
    content = f"""---
type: linkedin_post
timestamp: {datetime.now().isoformat()}
status: published
---
# LinkedIn Post
{text}
"""
    log_file.write_text(content, encoding='utf-8')
    print(f"[OK] Logged: {log_file.name}")


if __name__ == '__main__':
    text = sys.argv[1] if len(sys.argv) > 1 else f"🤖 AI Employee Post\n{datetime.now().strftime('%Y-%m-%d')}\n#AI #Automation"
    image = None
    if '--image' in sys.argv:
        idx = sys.argv.index('--image')
        if idx + 1 < len(sys.argv):
            image = sys.argv[idx + 1]
    
    success = auto_post(text, image)
    print("\n" + "=" * 60)
    print("✅ SUCCESS!" if success else "❌ FAILED!")
    print("=" * 60)
