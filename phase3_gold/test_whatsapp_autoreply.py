"""
WhatsApp Auto-Reply Test - Fixed
Tests message detection and auto-reply
"""
from playwright.sync_api import sync_playwright
import os
import shutil
import time

SESSION_DIR = os.path.join(os.path.dirname(__file__), "whatsapp_session_clean")

def clean_session():
    """Clean session directory if exists."""
    if os.path.exists(SESSION_DIR):
        try:
            shutil.rmtree(SESSION_DIR, ignore_errors=True)
            print("[*] Cleaned old session")
        except Exception as e:
            print(f"[!] Session cleanup warning: {e}")

def send_reply(page, message):
    """Send a reply message."""
    # Multiple selector strategies for message input
    input_selectors = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][role="textbox"]',
        'footer div[contenteditable="true"]',
        'div._ajwt div[contenteditable="true"]',
        'div[role="textbox"]'
    ]
    
    for selector in input_selectors:
        input_box = page.query_selector(selector)
        if input_box:
            try:
                input_box.fill(message)
                time.sleep(0.5)
                page.keyboard.press("Enter")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"[!] Send failed: {e}")
                return False
    
    print("[!] Message input not found")
    return False

def check_messages(page):
    """Check for unread messages in current chat."""
    # Message bubble selectors
    msg_selectors = [
        'div[data-testid="message-in"]',
        'div.message-in',
        'div._ai2r',
        'span[data-testid="message-in"] span[dir="auto"]'
    ]
    
    messages = []
    for selector in msg_selectors:
        items = page.query_selector_all(selector)
        if items:
            print(f"[OK] Found {len(items)} messages")
            for msg in items[-5:]:  # Last 5 messages
                try:
                    text = msg.inner_text().strip()
                    if text:
                        messages.append(text)
                except:
                    pass
            break
    
    return messages

def check_unread_chats(page):
    """Check for chats with unread messages."""
    chat_selectors = [
        'div[role="row"]',
        'div[role="listitem"]',
        'div[data-testid="chat-item"]',
        'div[data-testid="cell-frame"]'
    ]
    
    unread_chats = []
    
    for selector in chat_selectors:
        chats = page.query_selector_all(selector)
        if chats:
            print(f"[OK] Found {len(chats)} chats")
            for chat in chats[:10]:
                try:
                    # Check for unread badge
                    badge = chat.query_selector('span[data-testid="unread-count"]')
                    if badge:
                        count = badge.inner_text()
                        if count:
                            name_elem = chat.query_selector('span[dir="auto"]')
                            name = name_elem.inner_text()[:30] if name_elem else "Unknown"
                            unread_chats.append((name, count))
                except:
                    pass
            break
    
    return unread_chats

def main():
    print("=" * 60)
    print("WhatsApp Auto-Reply Test")
    print("=" * 60)
    
    clean_session()
    
    playwright = sync_playwright().start()
    
    print("\n[1] Launching browser...")
    try:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu'
            ]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        print("[OK] Browser launched!")
    except Exception as e:
        print(f"[ERROR] Launch failed: {e}")
        print("\nTrying without session...")
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu'
            ]
        )
        page = browser.new_page()
        print("[OK] Browser launched (no session)!")
    
    print("[2] Opening WhatsApp Web...")
    page.goto("https://web.whatsapp.com/", timeout=60000)
    
    print("[3] Waiting for login (45 seconds)...")
    print("    [!] SCAN QR CODE NOW!")
    page.wait_for_timeout(45000)
    
    # Check login
    is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
    if not is_logged_in:
        print("\n[!] Not logged in. Waiting 30 more seconds...")
        page.wait_for_timeout(30000)
        is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
        if not is_logged_in:
            print("\n[!] Login failed. Exiting...")
            browser.close()
            playwright.stop()
            return
    
    print("\n[OK] Logged in!")
    page.screenshot(path="whatsapp_logged_in.png")
    
    # Check unread chats
    print("\n[4] Checking unread chats...")
    unread = check_unread_chats(page)
    if unread:
        print(f"[!] Found {len(unread)} chats with unread messages:")
        for name, count in unread:
            print(f"    - {name}: {count} unread")
    else:
        print("[INFO] No unread chats found")
    
    # Open specific chat
    TEST_NUMBER = "923182383594"
    print(f"\n[5] Opening chat with {TEST_NUMBER}...")
    chat_url = f"https://web.whatsapp.com/send?phone={TEST_NUMBER}"
    page.goto(chat_url, timeout=60000)
    page.wait_for_timeout(10000)
    page.screenshot(path="whatsapp_chat_open.png")
    
    # Check messages
    print("\n[6] Checking messages in chat...")
    messages = check_messages(page)
    if messages:
        print(f"[OK] Found {len(messages)} messages:")
        for msg in messages:
            print(f"    - {msg[:60]}...")
    else:
        print("[INFO] No messages found in chat")
    
    # Test reply
    print("\n[7] Testing auto-reply...")
    test_reply = "Thanks for your message! 🤖 Humara team jald reply karega."
    if send_reply(page, test_reply):
        print("[OK] Reply sent!")
        page.screenshot(path="whatsapp_reply_sent.png")
    else:
        print("[!] Reply failed")
    
    print("\n[*] Browser open for 20 seconds to verify...")
    page.wait_for_timeout(20000)
    
    browser.close()
    playwright.stop()
    print("\n[OK] Done!")

if __name__ == "__main__":
    main()
