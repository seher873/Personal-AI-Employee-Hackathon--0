"""
Instagram Post - Browser Based (No API Token Needed)
Uses Playwright to login and post directly
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
    from config import IG_USERNAME, IG_PASSWORD
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Configuration
SESSION_DIR = "./ig_browser_session"
IMAGE_PATH = "./post_image.png"
CAPTION = "AI Employee is ready to work! #AI #Automation #Productivity"

print("=" * 60)
print("Instagram Browser Post")
print("=" * 60)

print(f"\n[*] Username: {IG_USERNAME}")
print(f"[*] Image: {IMAGE_PATH}")
print(f"[*] Caption: {CAPTION}")

if not os.path.exists(IMAGE_PATH):
    print(f"\n[ERROR] Image not found: {IMAGE_PATH}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Browser will open - Login if needed")
print("=" * 60)

playwright = sync_playwright().start()

try:
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # Navigate to Instagram
    print("\n[1] Opening Instagram...")
    page.goto("https://www.instagram.com/", timeout=60000)
    time.sleep(5)
    
    # Check if logged in
    print("[2] Checking login status...")
    time.sleep(3)
    
    # Try to detect if login needed
    url = page.url
    if "login" in url.lower() or "accounts" in url.lower():
        print("[!] Login required - entering credentials...")
        
        # Wait for login form
        time.sleep(3)
        
        # Fill username
        try:
            username_input = page.query_selector('input[name="username"]')
            if username_input:
                username_input.fill(IG_USERNAME)
                print("[OK] Username entered")
                time.sleep(1)
        except Exception as e:
            print(f"[!] Username input failed: {e}")
        
        # Fill password
        try:
            password_input = page.query_selector('input[name="password"]')
            if password_input:
                password_input.fill(IG_PASSWORD)
                print("[OK] Password entered")
                time.sleep(1)
        except Exception as e:
            print(f"[!] Password input failed: {e}")
        
        # Click login
        try:
            login_btn = page.query_selector('button[type="submit"]')
            if login_btn:
                login_btn.click()
                print("[OK] Login button clicked")
                time.sleep(8)
        except Exception as e:
            print(f"[!] Login button failed: {e}")
        
        # Handle "Save info" popup
        try:
            not_now = page.query_selector('button:has-text("Not Now"), button:has-text("Save")')
            if not_now:
                not_now.click()
                time.sleep(2)
        except:
            pass
        
        # Handle notifications
        try:
            notif_btn = page.query_selector('button:has-text("Allow"), button:has-text("Not Now")')
            if notif_btn:
                notif_btn.click()
                time.sleep(2)
        except:
            pass
    
    print("\n[OK] Logged in!")
    page.screenshot(path="ig_logged_in.png")
    
    # Click Create Post
    print("\n[3] Creating new post...")
    time.sleep(3)
    
    # Multiple selector strategies for Create button
    create_selectors = [
        'div[role="button"]:has-text("New")',
        'svg[aria-label="New post"]',
        '[aria-label="Create"]',
        'svg path[d*="M20.5 11.5c0-.8-.7-1.5-1.5-1.5H15V6c0-.8-.7-1.5-1.5-1.5S12 5.2 12 6v4H8c-.8 0-1.5.7-1.5 1.5S7.2 13 8 13h4v4c0 .8.7 1.5 1.5 1.5s1.5-.7 1.5-1.5v-4h4c.8 0 1.5-.7 1.5-1.5z"]'
    ]
    
    clicked = False
    for selector in create_selectors:
        try:
            create_btn = page.query_selector(selector)
            if create_btn:
                create_btn.click()
                print("[OK] Create button clicked")
                time.sleep(4)
                clicked = True
                break
        except:
            continue
    
    if not clicked:
        print("[!] Create button not found - manual action needed")
        print("    Please click 'New' or '+' button manually")
        time.sleep(10)
    
    # Upload image
    print("\n[4] Uploading image...")
    time.sleep(3)
    
    try:
        file_input = page.query_selector('input[type="file"]')
        if file_input:
            file_input.set_input_files(IMAGE_PATH)
            print("[OK] Image uploaded")
            time.sleep(6)
        else:
            print("[!] File input not found")
    except Exception as e:
        print(f"[!] Upload failed: {e}")
    
    # Click Next (crop)
    print("\n[5] Clicking Next (crop)...")
    time.sleep(2)
    
    try:
        next_btn = page.query_selector('button:has-text("Next")')
        if next_btn:
            next_btn.click()
            print("[OK] Next clicked")
            time.sleep(4)
    except Exception as e:
        print(f"[!] Next failed: {e}")
    
    # Click Next (filters) if visible
    time.sleep(2)
    try:
        next_btn2 = page.query_selector('button:has-text("Next")')
        if next_btn2 and next_btn2.is_visible():
            next_btn2.click()
            print("[OK] Next (filters) clicked")
            time.sleep(3)
    except:
        pass
    
    # Type caption
    print(f"\n[6] Adding caption: {CAPTION[:40]}...")
    time.sleep(2)
    
    try:
        caption_box = page.query_selector('[aria-label="Write a caption..."], [placeholder="Write a caption..."], textarea')
        if caption_box:
            caption_box.fill(CAPTION)
            print("[OK] Caption added")
            time.sleep(2)
    except Exception as e:
        print(f"[!] Caption failed: {e}")
    
    # Click Share
    print("\n[7] Clicking Share...")
    time.sleep(2)
    
    try:
        share_btn = page.query_selector('button:has-text("Share")')
        if share_btn:
            share_btn.click()
            print("[OK] Share button clicked")
            time.sleep(8)
        else:
            print("[!] Share button not found")
    except Exception as e:
        print(f"[!] Share failed: {e}")
    
    print("\n" + "=" * 60)
    print("[OK] Post process completed!")
    print("=" * 60)
    
    page.screenshot(path="ig_post_done.png")
    
    print("\n[*] Browser open for 20 seconds - verify post on Instagram")
    time.sleep(20)
    
    browser.close()
    playwright.stop()
    
    print("\n[OK] Done!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    browser.close()
    playwright.stop()
