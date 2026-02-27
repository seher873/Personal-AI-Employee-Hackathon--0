"""
Gmail Manual Login - Run once to save session
"""

import os
import json
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = "./gmail_session"
STORAGE_FILE = os.path.join(SESSION_DIR, "storage_state.json")

os.makedirs(SESSION_DIR, exist_ok=True)

print("=" * 60)
print("Gmail Manual Login")
print("=" * 60)
print("\nA browser will open. Please:")
print("1. Sign in to Gmail manually")
print("2. Wait until you see your inbox")
print("3. Session auto-saves after 60 seconds or when inbox detected\n")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    
    context = browser.new_context(
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    
    print("Navigating to Gmail...")
    page.goto("https://mail.google.com", wait_until="domcontentloaded")
    
    # Wait up to 60 seconds for inbox to appear
    print("Waiting for login... (max 60 seconds)")
    logged_in = False
    for i in range(60):
        try:
            # Check for inbox elements
            if page.is_visible("[aria-label='Inbox']", timeout=1000) or \
               page.is_visible("[role='main']", timeout=1000):
                print("✅ Inbox detected!")
                logged_in = True
                time.sleep(3)  # Wait a bit more for full load
                break
        except:
            pass
        time.sleep(1)
        if i % 10 == 9:
            print(f"  ... waiting ({i+1}s)")
    
    # Save session
    storage = context.storage_state()
    with open(STORAGE_FILE, 'w') as f:
        json.dump(storage, f)
    
    print(f"\n✅ Session saved to: {STORAGE_FILE}")
    print("You can now run gmail_watcher.py - it will use this saved session!")
    
    browser.close()
