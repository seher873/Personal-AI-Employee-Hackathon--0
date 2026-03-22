"""
Instagram Post Helper
Opens Instagram with saved session - you manually create post
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[ERROR] Playwright not installed. Run: py -m pip install playwright")
    sys.exit(1)

SESSION_DIR = "./ig_browser_session"

print("=" * 60)
print("Instagram Post Helper")
print("=" * 60)

print("\n[*] Opening Instagram with saved session...")
print("[*] You can manually create a post")
print("[*] Image: ./pictures/ai-employee.jpg")
print("[*] Caption: AI Employee is ready to work! #AI #Automation #Productivity")
print("\n" + "=" * 60)

playwright = sync_playwright().start()

try:
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("\n[1] Opening Instagram...")
    page.goto("https://www.instagram.com/", timeout=60000)
    
    print("\n" + "=" * 60)
    print("MANUAL POST STEPS:")
    print("=" * 60)
    print("1. Click 'New' or '+' button (top right)")
    print("2. Select: ./pictures/ai-employee.jpg")
    print("3. Click 'Next'")
    print("4. Click 'Next' again")
    print("5. Add caption: AI Employee is ready to work! #AI #Automation #Productivity")
    print("6. Click 'Share'")
    print("=" * 60)
    
    print("\n[*] Browser open for 60 seconds - create your post!")
    
    # Keep browser open
    for i in range(60, 0, -1):
        sys.stdout.write(f"\r    Time remaining: {i} seconds")
        sys.stdout.flush()
        time.sleep(1)
    
    print("\n\n[*] Keeping browser open - close manually when done")
    input("Press Enter to close browser...")
    
    browser.close()
    playwright.stop()
    
    print("\n[OK] Done!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    browser.close()
    playwright.stop()
