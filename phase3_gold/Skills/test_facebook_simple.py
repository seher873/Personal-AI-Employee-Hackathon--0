#!/usr/bin/env python3
"""
Simple Facebook Post Test - Windows Compatible
No unicode emojis
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
from config import FB_EMAIL, FB_PASSWORD

SCREENSHOTS_DIR = Path(__file__).parent.parent / "Screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("FACEBOOK SIMPLE POST TEST")
print("=" * 60)
print(f"Email: {FB_EMAIL}")
print("=" * 60)

try:
    with sync_playwright() as p:
        # Launch with user data dir for persistent session
        user_data_dir = Path(__file__).parent / "fb_session" / "chrome_user_data"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        browser = p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            viewport={"width": 1280, "height": 720}
        )
        
        page = browser.pages[0]
        
        # Navigate
        print("\n[1/4] Navigating to Facebook...")
        page.goto("https://www.facebook.com", timeout=60000)
        time.sleep(5)
        
        # Check if logged in
        print("[2/4] Checking login...")
        is_logged_in = page.is_visible("[data-pagelet='MainFeed']", timeout=5000)
        
        if is_logged_in:
            print("[OK] Already logged in!")
        else:
            print("[INFO] Not logged in. Please login manually in the browser.")
            print("[INFO] Waiting 60 seconds for manual login...")
            time.sleep(60)
        
        # Take screenshot
        screenshot = SCREENSHOTS_DIR / "fb_login_status.png"
        page.screenshot(path=str(screenshot))
        print(f"[OK] Screenshot saved: {screenshot}")
        
        # Try to post
        print("\n[3/4] Creating post...")
        test_text = f"AI Employee Test - {time.strftime('%Y-%m-%d %H:%M')} - Automated posting test!"
        
        # Press 'n' to open composer
        page.keyboard.press('n')
        time.sleep(3)
        
        # Find and fill text area
        text_entered = False
        for selector in ["[data-contents='true']", "[role='textbox']", "div[contenteditable='true']"]:
            try:
                text_area = page.locator(selector).first
                text_area.wait_for(state='visible', timeout=3000)
                text_area.fill(test_text)
                print(f"[OK] Text entered using: {selector}")
                text_entered = True
                break
            except:
                continue
        
        if not text_entered:
            print("[WARN] Could not enter text automatically")
        
        screenshot = SCREENSHOTS_DIR / "fb_composer.png"
        page.screenshot(path=str(screenshot))
        print(f"[OK] Screenshot saved: {screenshot}")
        
        # Click Post
        print("\n[4/4] Posting...")
        post_clicked = False
        for selector in ['button:has-text("Post")', 'button:has-text("Share")', '[aria-label="Post"]']:
            try:
                post_btn = page.locator(selector).first
                post_btn.wait_for(state='visible', timeout=3000)
                post_btn.click()
                print(f"[OK] Post button clicked: {selector}")
                post_clicked = True
                break
            except:
                continue
        
        if not post_clicked:
            print("[WARN] Could not click Post button")
        
        time.sleep(5)
        
        screenshot = SCREENSHOTS_DIR / "fb_posted.png"
        page.screenshot(path=str(screenshot))
        print(f"[OK] Final screenshot saved: {screenshot}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)
        print("\nCheck the screenshots in: Screenshots/")
        print("Browser will stay open for 30 more seconds...")
        time.sleep(30)
        
        browser.close()
        print("\n[OK] Done!")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
