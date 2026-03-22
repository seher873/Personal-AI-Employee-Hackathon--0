"""
WhatsApp Message Check - Updated Selectors
Tests new WhatsApp Web UI selectors
"""
import os
import sys
from playwright.sync_api import sync_playwright

print("=" * 60)
print("WhatsApp Message Check - Updated Selectors")
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

# Wait for user to select/open a chat
print("\n[*] Please select/open a chat in the browser...")
print("[*] Waiting 15 seconds for you to open a chat...")
page.wait_for_timeout(15000)

try:
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

    # NEW: Check for unread messages with updated selectors
    print("\n[4] Checking for UNREAD messages (NEW selectors)...")
    print("=" * 60)

    # Try multiple selector strategies
    selectors_to_try = [
        'div[role="row"]',           # Old selector
        'div[role="listitem"]',      # New selector
        'div[data-testid="chat-item"]',  # Alternative
        'div._ai2i',                 # Class-based (WhatsApp specific)
        'div[data-testid="cell-frame"]',  # Another alternative
    ]

    chat_items = []
    for selector in selectors_to_try:
        items = page.query_selector_all(selector)
        if items:
            print(f"[OK] Found chats with selector: {selector}")
            chat_items = items
            break

    if not chat_items:
        print("[!] No chats found with any selector")
        print("    Make sure you have contacts/chats in WhatsApp")
    else:
        print(f"[OK] Found {len(chat_items)} chats")

        unread_count = 0
        print("\n[*] Scanning first 20 chats...\n")

        for i, chat in enumerate(chat_items[:20]):
            try:
                # Get chat name - try multiple selectors
                chat_name = "Unknown"
                for name_selector in ['span[dir="auto"]', 'h3', 'div._aj7y']:
                    chat_name_elem = chat.query_selector(name_selector)
                    if chat_name_elem:
                        chat_name = chat_name_elem.inner_text()[:30]
                        break

                # Check for unread badge - try multiple selectors
                unread_badge = None
                for badge_selector in [
                    'span[data-testid="unread-count"]',
                    'span._ai2p',
                    'div[data-testid="unread-count"]',
                    'span.unread-count'
                ]:
                    unread_badge = chat.query_selector(badge_selector)
                    if unread_badge:
                        break

                if unread_badge:
                    unread_text = unread_badge.inner_text()
                    if unread_text:
                        unread_count += 1
                        print(f"[UNREAD #{unread_count}] {chat_name} - {unread_text} messages")
                else:
                    print(f"[READ] {chat_name}")
            except Exception as e:
                print(f"[ERROR] Failed to parse chat: {e}")

        print("\n" + "=" * 60)
        if unread_count > 0:
            print(f"\n[OK] Found {unread_count} chat(s) with unread messages!")
        else:
            print("\n[INFO] No unread messages found")
            print("    - All chats are read, OR")
            print("    - No messages in selected chat, OR")
            print("    - Selectors need more updates")

    # NEW: Check currently open chat for messages
    print("\n[5] Checking currently open chat...")
    print("=" * 60)

    # Try to find message bubbles in open chat
    message_selectors = [
        'div[data-testid="message-in"]',      # Incoming messages
        'div.message-in',                      # Alternative
        'div._ai2r',                          # Class-based
        'div[data-testid="cell-frame"] span[dir="auto"]',  # Message text
    ]

    for msg_selector in message_selectors:
        messages = page.query_selector_all(msg_selector)
        if messages:
            print(f"[OK] Found {len(messages)} messages with selector: {msg_selector}")
            # Show last 3 messages
            for msg in messages[-3:]:
                try:
                    msg_text = msg.inner_text()[:100]
                    if msg_text.strip():
                        print(f"    - {msg_text}")
                except:
                    pass
            break
    else:
        print("[INFO] No messages detected in open chat")
        print("    Make sure a chat is open with messages")

    print("\n[*] Browser will stay open for 30 seconds...")
    print("    You can manually inspect elements using DevTools (F12)")
    page.wait_for_timeout(30000)

except Exception as e:
    print(f"\n[!] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[6] Closing...")
browser.close()
playwright.stop()

print("\n[OK] Done!")
