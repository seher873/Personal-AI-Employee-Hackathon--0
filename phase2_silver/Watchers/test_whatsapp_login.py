#!/usr/bin/env python3
"""
Quick WhatsApp Login Test
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("WhatsApp Login Test")
print("=" * 60)

with sync_playwright() as p:
    print("\n[1] Launching browser with saved session...")
    
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,  # Visible browser
        timeout=30000,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
        ]
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    print("[2] Opening WhatsApp Web...")
    page.goto("https://web.whatsapp.com", timeout=60000)
    
    print("[3] Waiting for page load (15 seconds)...")
    time.sleep(15)
    
    # Check login status
    print("\n[4] Checking login status...")
    
    logged_in_selectors = [
        'div[data-testid="default-user"]',
        'div[data-testid="chat-list"]',
        'span[title="Status"]',
    ]
    
    is_logged = False
    for selector in logged_in_selectors:
        try:
            if page.locator(selector).first.is_visible(timeout=3000):
                print(f"✅ LOGGED IN! (detected: {selector})")
                is_logged = True
                break
        except:
            pass
    
    if is_logged:
        print("\n" + "=" * 60)
        print("✅ WHATSAPP IS LOGGED IN!")
        print("=" * 60)
        print("\nSession is working. You can now run:")
        print("  py Watchers\\whatsapp_watcher_autoreply.py")
    else:
        print("\n" + "=" * 60)
        print("❌ NOT LOGGED IN")
        print("=" * 60)
        print("\nQR Code screen is showing.")
        print("Please scan QR code with your phone.")
        print("\nWaiting 60 seconds for QR scan...")
        
        for i in range(60, 0, -1):
            time.sleep(1)
            if i % 10 == 0:
                print(f"  {i}s remaining...")
        
        # Check again
        for selector in logged_in_selectors:
            try:
                if page.locator(selector).first.is_visible(timeout=3000):
                    print(f"\n✅ Login detected!")
                    is_logged = True
                    break
            except:
                pass
    
    # Take screenshot
    screenshot_path = Path(__file__).parent / "whatsapp_status.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"\n[5] Screenshot saved: {screenshot_path}")
    
    print("\n[*] Browser will close in 10 seconds...")
    time.sleep(10)
    
    context.close()

print("\n[OK] Done!")
