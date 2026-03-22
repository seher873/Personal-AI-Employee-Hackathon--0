#!/usr/bin/env python3
"""
LinkedIn Quick Post - Simple Browser Auto Post
Opens LinkedIn with pre-filled post content
"""

import os
import sys
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def quick_post(text: str, image_path: str = None):
    """Open LinkedIn and create post with pre-filled text"""
    print("=" * 60)
    print("LinkedIn Quick Post")
    print("=" * 60)
    print(f"\nPost content:\n{text}\n")
    print("[*] Opening LinkedIn in browser...")
    print("[*] The post composer will open with your text pre-filled")
    print("[*] Click 'Post' button when ready\n")
    
    session_dir = Path(__file__).parent / 'linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state = session_dir / 'state.json'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            # Try to load saved session
            if storage_state.exists():
                print("[OK] Loading saved session...")
                context = browser.new_context(storage_state=storage_state)
            else:
                print("[INFO] No saved session - you'll need to login")
                context = browser.new_context()
            
            page = context.new_page()
            page.goto('https://www.linkedin.com/feed/?createPost=true', timeout=60000)
            time.sleep(3)
            
            # Try to fill the text
            try:
                editor = page.locator('div[contenteditable="true"][role="textbox"]').first
                editor.wait_for(timeout=5000)
                editor.fill(text)
                print("[OK] Text filled in composer")
                
                if image_path and os.path.exists(image_path):
                    media_input = page.locator('input[type="file"][accept*="image"]').first
                    media_input.set_input_files(image_path)
                    print(f"[OK] Image added: {image_path}")
            except Exception as e:
                print(f"[INFO] You'll need to paste the text manually: {e}")
            
            print("\n[*] Browser is ready - complete the post manually")
            print("[*] Close browser when done")
            
            # Keep browser open
            while context.pages:
                time.sleep(1)
            
            browser.close()
            
            # Save log
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
    log_file = log_dir / f'{timestamp}_linkedin_quick_post.md'
    
    content = f"""---
type: linkedin_quick_post
timestamp: {datetime.now().isoformat()}
status: posted
---

# LinkedIn Quick Post

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{text}

## Media
{'Image: ' + image_path if image_path else 'None'}
"""
    log_file.write_text(content, encoding='utf-8')


def main():
    default_text = f"""🤖 AI Employee Auto Post

Testing LinkedIn automation.
{datetime.now().strftime('%Y-%m-%d %H:%M')}

#AI #Automation #LinkedIn"""
    
    text = sys.argv[1] if len(sys.argv) > 1 else default_text
    image_path = None
    
    if '--image' in sys.argv:
        idx = sys.argv.index('--image')
        if idx + 1 < len(sys.argv):
            image_path = sys.argv[idx + 1]
    
    quick_post(text, image_path)


if __name__ == '__main__':
    main()
