#!/usr/bin/env python3
"""
Facebook Debug Test - Full Verification
Opens browser, posts, and verifies with screenshots
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
print("FACEBOOK DEBUG TEST - Full Verification")
print("=" * 60)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        # Step 1: Navigate
        print("\n[1/6] Navigating to Facebook...")
        page.goto("https://www.facebook.com", timeout=60000)
        time.sleep(5)
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_loaded.png"))
        
        # Step 2: Check login
        print("[2/6] Checking login status...")
        if page.is_visible("[data-pagelet='MainFeed']", timeout=5000):
            print("✅ Already logged in")
        else:
            print("⚠️ Not logged in - waiting for manual login...")
            time.sleep(10)
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_logged_in.png"))
        
        # Step 3: Open composer
        print("[3/6] Opening composer...")
        
        # Try keyboard shortcut first
        print("  Trying keyboard shortcut 'n'...")
        page.keyboard.press('n')
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_composer_open.png"))
        
        # Step 4: Type text
        print("[4/6] Typing post text...")
        test_text = f"DEBUG POST - {time.strftime('%H:%M')} - Testing automation"
        
        # Try multiple text areas
        text_selectors = [
            "[data-contents='true']",
            "[role='textbox']",
            "div[contenteditable='true']",
        ]
        
        for selector in text_selectors:
            try:
                text_area = page.locator(selector).first
                text_area.wait_for(state='visible', timeout=3000)
                text_area.fill(test_text)
                print(f"  ✅ Text entered using: {selector}")
                break
            except:
                continue
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_text_entered.png"))
        time.sleep(2)
        
        # Step 5: Click Post button
        print("[5/6] Clicking Post button...")
        
        post_selectors = [
            'button:has-text("Post")',
            'button:has-text("Share")',
            '[aria-label="Post"]',
        ]
        
        for selector in post_selectors:
            try:
                post_btn = page.locator(selector).first
                post_btn.wait_for(state='visible', timeout=3000)
                post_btn.click()
                print(f"  ✅ Post button clicked: {selector}")
                break
            except:
                continue
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_post_clicked.png"))
        
        # Step 6: Wait and verify
        print("[6/6] Waiting for post to publish...")
        time.sleep(10)
        
        # Check for success
        success_found = False
        success_indicators = ["Your post was shared", "Posted", "Share now"]
        
        for indicator in success_indicators:
            try:
                if page.is_visible(f'div:has-text("{indicator}")', timeout=3000):
                    print(f"  ✅ Success indicator found: {indicator}")
                    success_found = True
                    break
            except:
                continue
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_final.png"))
        
        # Final verification - go to profile
        print("\n[VERIFICATION] Going to your profile to check post...")
        page.goto("https://www.facebook.com/me", timeout=60000)
        time.sleep(5)
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_profile.png"))
        
        # Check if test post is visible
        try:
            if page.is_visible(f'div:has-text("DEBUG POST")', timeout=5000):
                print("✅ POST VISIBLE ON PROFILE!")
            else:
                print("⚠️ Post not visible on profile")
        except:
            print("⚠️ Could not verify post on profile")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)
        print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}")
        print("\nPlease check these screenshots:")
        print("  1. 06_final.png - After post click")
        print("  2. 07_profile.png - Your profile with post")
        print("\nOpen Facebook manually and check if post is visible!")
        
        print("\nBrowser will stay open for 30 more seconds...")
        time.sleep(30)
        
        browser.close()
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
