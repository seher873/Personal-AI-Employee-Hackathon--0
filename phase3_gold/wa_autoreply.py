"""
WhatsApp Auto-Reply - Working Version with Proper Login Detection
"""
from playwright.sync_api import sync_playwright
import os
import time

SESSION_DIR = os.path.join(os.path.dirname(__file__), "wa_session")

print("=" * 60)
print("WhatsApp Auto-Reply & Message Detection")
print("=" * 60)

playwright = sync_playwright().start()

print("\n[1] Launching browser...")
browser = playwright.chromium.launch_persistent_context(
    user_data_dir=SESSION_DIR,
    headless=False,
    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
)

page = browser.pages[0] if browser.pages else browser.new_page()

print("[2] Opening WhatsApp Web...")
page.goto("https://web.whatsapp.com/", timeout=60000)

# Better login detection
print("\n" + "=" * 60)
print("SCAN QR CODE WITH YOUR PHONE")
print("=" * 60)
print("    Waiting up to 2 minutes...\n")

logged_in = False
for i in range(40):  # 40 * 3 = 120 seconds
    time.sleep(3)
    
    # Multiple ways to detect login
    try:
        # Method 1: Check if QR code is gone
        qr_code = page.query_selector('canvas')
        
        # Method 2: Check for chat list
        chat_list = page.query_selector('div[data-testid="default-user"]')
        
        # Method 3: Check for search box (appears after login)
        search_box = page.query_selector('div[role="search"]')
        
        # Method 4: Check for main app container
        app_main = page.query_selector('div[data-testid="list-pane"]')
        
        if chat_list is None and (search_box is not None or app_main is not None):
            print(f"\n[OK] Login detected! ({(i+1)*3}s)")
            logged_in = True
            break
        
        if i % 5 == 0:
            print(f"    Waiting... ({(i+1)*3}s)")
    except:
        continue

if not logged_in:
    print("\n[!] Login not detected in 2 minutes")
    print("    Keeping browser open for 30 more seconds...")
    time.sleep(30)
    browser.close()
    playwright.stop()
    exit(1)

# Wait for page to fully load
print("\n[*] Waiting for page to load...")
time.sleep(5)
page.screenshot(path="wa_main_screen.png")
print("[*] Screenshot: wa_main_screen.png")

# Check for unread chats
print("\n" + "=" * 60)
print("CHECKING UNREAD CHATS")
print("=" * 60)

chats = page.query_selector_all('div[role="row"]')
if not chats:
    chats = page.query_selector_all('div[role="listitem"]')

if chats:
    print(f"[*] Found {len(chats)} chats in list")
    
    unread = []
    for chat in chats[:20]:
        try:
            name_elem = chat.query_selector('span[dir="auto"]')
            name = name_elem.inner_text()[:30] if name_elem else "Unknown"
            
            badge = chat.query_selector('span[data-testid="unread-count"]')
            if badge:
                count = badge.inner_text()
                if count and count.isdigit():
                    unread.append((name, count))
                    print(f"    [UNREAD] {name}: {count}")
        except:
            continue
    
    if unread:
        print(f"\n[OK] {len(unread)} chats with unread messages!")
    else:
        print("\n[INFO] No unread messages")
else:
    print("[!] Could not detect chat list")

# Open first chat
print("\n" + "=" * 60)
print("OPENING CHAT")
print("=" * 60)

try:
    # Click first chat
    first_chat = chats[0] if chats else page.query_selector('div[role="row"]')
    if first_chat:
        first_chat.click()
        print("[*] Chat opened")
        time.sleep(3)
        page.screenshot(path="wa_chat_view.png")
except Exception as e:
    print(f"[!] Could not open chat: {e}")

# Read messages
print("\n" + "=" * 60)
print("READING MESSAGES")
print("=" * 60)

msgs = page.query_selector_all('div[data-testid="message-in"]')
if msgs:
    print(f"[*] Found {len(msgs)} incoming messages")
    for msg in msgs[-5:]:
        try:
            text = msg.inner_text().strip()
            if text:
                print(f"    - {text[:70]}...")
        except:
            pass
else:
    print("[INFO] No messages in this chat")

# Send reply
if msgs:
    print("\n" + "=" * 60)
    print("SENDING REPLY")
    print("=" * 60)
    
    reply = "Thanks for your message! 🤖 Humara team jald reply karega."
    print(f"    Message: {reply}")
    
    # Find input box
    input_box = page.query_selector('div[contenteditable="true"][data-tab="10"]')
    if not input_box:
        input_box = page.query_selector('div[contenteditable="true"][role="textbox"]')
    if not input_box:
        input_box = page.query_selector('footer div[contenteditable="true"]')
    
    if input_box:
        try:
            input_box.fill(reply)
            time.sleep(0.5)
            page.keyboard.press("Enter")
            time.sleep(1)
            print("[OK] Reply sent!")
            page.screenshot(path="wa_message_sent.png")
        except Exception as e:
            print(f"[!] Send failed: {e}")
    else:
        print("[!] Message input not found")

print("\n" + "=" * 60)
print("COMPLETE!")
print("=" * 60)
print("\n[*] Browser open for 20 seconds")
print("    Session saved - next run will be faster!")
time.sleep(20)

browser.close()
playwright.stop()
print("\n[OK] Done!")
