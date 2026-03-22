"""
Quick WhatsApp Unread Check
Tests unread message detection
"""
import os
from playwright.sync_api import sync_playwright

print("=" * 60)
print("WhatsApp Unread Message Check")
print("=" * 60)

playwright = sync_playwright().start()

browser = playwright.chromium.launch_persistent_context(
    user_data_dir="./whatsapp_session",
    headless=False,
    args=['--disable-blink-features=AutomationControlled']
)

page = browser.new_page()
page.goto("https://web.whatsapp.com/", timeout=60000)

print("\n[*] Waiting 15 seconds for page load...")
page.wait_for_timeout(15000)

# Check login
is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
if not is_logged_in:
    print("[!] Not logged in!")
    page.wait_for_timeout(30000)

print("\n[OK] Logged in!")

# Find all chat rows
chat_rows = page.query_selector_all('div[role="row"]')
print(f"\n[OK] Found {len(chat_rows)} chats")

print("\n" + "=" * 60)
print("Scanning chats for unread messages...")
print("=" * 60)

for i, chat in enumerate(chat_rows[:10]):
    try:
        # Get chat name
        name_elem = chat.query_selector('span[dir="auto"]')
        chat_name = name_elem.inner_text() if name_elem else "Unknown"
        
        # Try to find unread count with multiple selectors
        unread = None
        for selector in [
            'span[data-testid="unread-count"]',
            'div[data-testid="unread-count"]',
            'span[aria-label*="unread"]',
            'div[aria-label*="unread"]',
        ]:
            unread = chat.query_selector(selector)
            if unread:
                break
        
        if unread:
            unread_text = unread.inner_text()
            print(f"\n[UNREAD] {chat_name} - {unread_text} messages")
        else:
            # Check for green dot (unread indicator)
            green_dot = chat.query_selector('span[style*="background-color"]')
            if green_dot:
                print(f"\n[NEW] {chat_name} - Has new indicator")
            else:
                print(f"[READ] {chat_name}")
                
        # Get last message
        all_spans = chat.query_selector_all('span')
        for span in all_spans:
            try:
                text = span.inner_text()
                if text and len(text) > 5 and len(text) < 100:
                    # Skip name and time
                    if text != chat_name and not text.startswith(('AM', 'PM', '202')):
                        print(f"       Last: {text[:60]}")
                        break
            except:
                pass
                
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n[*] Browser open for 20 more seconds...")
page.wait_for_timeout(20000)

browser.close()
playwright.stop()

print("\n[OK] Done!")
