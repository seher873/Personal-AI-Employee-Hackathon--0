"""
Gmail Manual Login - Run once to save session
Uses Chrome with user data for better stealth.
"""

import os
import sys
import json
import time
import codecs

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from playwright.sync_api import sync_playwright

SESSION_DIR = "./gmail_session"
STORAGE_FILE = os.path.join(SESSION_DIR, "storage_state.json")
USER_DATA_DIR = os.path.join(SESSION_DIR, "chrome_user_data")

os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

print("=" * 60)
print("Gmail Manual Login - Stealth Mode")
print("=" * 60)
print("\nIMPORTANT: If Google blocks login, try these:")
print("1. Use a different browser (Chrome/Edge)")
print("2. Enable 2FA and use App Password")
print("3. Login normally in Chrome first, then run this script")
print("4. Try again after a few hours")
print("\nA browser will open. Please:")
print("1. Sign in to Gmail manually")
print("2. Complete any 2FA verification")
print("3. Wait until you see your inbox")
print("4. Session auto-saves after login detected\n")

with sync_playwright() as p:
    # Launch Chrome with user data directory for persistence
    browser = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            "--allow-running-insecure-content",
        ],
        viewport={"width": 1280, "height": 720}
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    print("Navigating to Gmail...")
    page.goto("https://accounts.google.com", wait_until="domcontentloaded")

    # Bypass automation detection
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """)

    # Wait up to 120 seconds for inbox to appear
    print("Waiting for login... (max 120 seconds)")
    logged_in = False
    for i in range(120):
        try:
            # Check for inbox elements
            if page.is_visible("[aria-label='Inbox']", timeout=1000) or \
               page.is_visible("[role='main']", timeout=1000) or \
               page.url.startswith("https://mail.google.com"):
                print("✅ Inbox detected!")
                logged_in = True
                time.sleep(5)  # Wait a bit more for full load
                break
        except:
            pass
        time.sleep(1)
        if i % 10 == 9:
            print(f"  ... waiting ({i+1}s)")

    # Save session
    storage = browser.storage_state()
    with open(STORAGE_FILE, 'w') as f:
        json.dump(storage, f)

    print(f"\n✅ Session saved to: {STORAGE_FILE}")
    print(f"✅ Chrome profile saved to: {USER_DATA_DIR}")
    print("\nYou can now run gmail_watcher.py - it will use this saved session!")
    print("\nTIP: If login fails, try logging into Gmail in regular Chrome first,")
    print("then run this script again. The browser profile will be reused.")

    browser.close()
