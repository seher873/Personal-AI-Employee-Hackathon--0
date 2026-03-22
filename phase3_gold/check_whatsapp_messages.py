"""
Quick WhatsApp Message Check
"""
import os
import sys
from playwright.sync_api import sync_playwright

print("=" * 60)
print("WhatsApp Message Check")
print("=" * 60)

print("\n[1] Launching browser...")
playwright = sync_playwright().start()

browser = playwright.chromium.launch_persistent_context(
    user_data_dir="./whatsapp_session",
    headless=False,
    args=['--disable-blink-features=AutomationControlled']
)

print("[2] Opening WhatsApp Web...")
page = browser.new_page()
page.goto("https://web.whatsapp.com/", timeout=60000)

print("[3] Waiting for page load...")
page.wait_for_timeout(10000)

print("\n[OK] WhatsApp Web is open!")

# Wait for user to select a chat
print("\n[*] Please select/open a chat in the browser...")
print("[*] Waiting 15 seconds for you to open a chat...")
page.wait_for_timeout(15000)

# Try to detect messages
print("\n[4] Detecting messages...")
try:
    # Wait for message elements to load
    page.wait_for_timeout(5000)
    
    # Check if logged in
    is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
    
    if not is_logged_in:
        print("\n[!] WhatsApp Web is NOT logged in!")
        print("    Please scan QR code in the browser")
        page.wait_for_timeout(30000)
        is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
        if not is_logged_in:
            print("\n[!] Still not logged in. Closing...")
            browser.close()
            playwright.stop()
            sys.exit(1)
    
    print("\n[OK] Logged in!")
    
    # Take screenshot for debugging
    print("[*] Taking screenshot...")
    page.screenshot(path="whatsapp_debug.png")
    print("    Saved: whatsapp_debug.png")
    
    # Check for unread messages in chat list
    print("\n[5] Checking for UNREAD messages in chat list...")
    print("=" * 60)
    
    # Find all chat items in the sidebar
    chat_items = page.query_selector_all('div[role="row"]')
    
    unread_count = 0
    print("\n[*] Scanning chats...\n")
    
    for i, chat in enumerate(chat_items[:20]):  # Check first 20 chats
        try:
            # Get chat name
            chat_name_elem = chat.query_selector('span[dir="auto"]')
            chat_name = chat_name_elem.inner_text() if chat_name_elem else "Unknown"
            
            # Check for unread badge
            unread_badge = chat.query_selector('span[data-testid="unread-count"]')
            
            if unread_badge:
                unread_text = unread_badge.inner_text()
                if unread_text:
                    unread_count += 1
                    print(f"[UNREAD #{unread_count}] {chat_name} - {unread_text} messages")
                    
                    # Get last message preview
                    last_msg_elem = chat.query_selector('span[data-testid="last-message-content"]')
                    if last_msg_elem:
                        last_msg = last_msg_elem.inner_text()[:50]
                        print(f"              Preview: {last_msg}")
                    print()
        except Exception as e:
            pass
    
    print("=" * 60)
    if unread_count > 0:
        print(f"\n[OK] Found {unread_count} chat(s) with unread messages!")
    else:
        print("\n[!] No unread messages found")
        print("    All chats are read or no new messages")
    
    print("\n[*] Keeping browser open for 20 more seconds...")
    print("    You can manually check messages in the browser")
    page.wait_for_timeout(20000)

except Exception as e:
    print(f"\n[!] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[6] Closing...")
browser.close()
playwright.stop()

print("\n[OK] Done!")
