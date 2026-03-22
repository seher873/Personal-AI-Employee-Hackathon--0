"""
WhatsApp Auto-Reply - Interactive Test
Manually select chat, then auto-detect and reply
"""
from playwright.sync_api import sync_playwright
import os
import time

SESSION_DIR = os.path.join(os.path.dirname(__file__), "whatsapp_session")

print("=" * 60)
print("WhatsApp Auto-Reply - Interactive")
print("=" * 60)
print("\nInstructions:")
print("1. Scan QR code to login")
print("2. Manually open/select a chat")
print("3. Script will auto-detect and reply")
print("=" * 60)

playwright = sync_playwright().start()

print("\n[1] Launching browser with session...")
browser = playwright.chromium.launch_persistent_context(
    user_data_dir=SESSION_DIR,
    headless=False,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox'
    ]
)

page = browser.pages[0] if browser.pages else browser.new_page()

print("[2] Opening WhatsApp Web...")
page.goto("https://web.whatsapp.com/", timeout=60000)

print("[3] Waiting for login (60 seconds)...")
print("    [!] SCAN QR CODE NOW!")

# Wait for login - check every 5 seconds
for i in range(12):
    time.sleep(5)
    is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
    if is_logged_in:
        print(f"\n[OK] Logged in at attempt {i+1}!")
        page.screenshot(path="whatsapp_logged_in.png")
        break
    print(f"    Waiting... ({(i+1)*5}s)")
else:
    print("\n[!] Login timeout. Please scan QR code!")
    print("    Keeping browser open for manual login...")
    time.sleep(60)

# Now wait for user to open a chat
print("\n" + "=" * 60)
print("[4] PLEASE OPEN A CHAT MANUALLY")
print("=" * 60)
print("    Click on any chat in the left panel")
print("    Script will detect and reply in 20 seconds...")
print("=" * 60)

for i in range(20, 0, -1):
    print(f"    Opening chat in {i}s...")
    time.sleep(1)

page.screenshot(path="whatsapp_chat_selected.png")
print("\n[*] Screenshot saved: whatsapp_chat_selected.png")

# Detect messages
print("\n[5] Detecting messages...")

message_selectors = [
    ('div[data-testid="message-in"]', 'data-testid'),
    ('div.message-in', 'class'),
    ('span[data-testid="message-in"] span[dir="auto"]', 'nested'),
    ('div._ai2r', 'class_old'),
]

messages = []
for selector, stype in message_selectors:
    try:
        items = page.query_selector_all(selector)
        if items:
            print(f"[OK] Found {len(items)} messages (selector: {stype})")
            for msg in items[-10:]:
                try:
                    text = msg.inner_text().strip()
                    if text and len(text) > 0:
                        messages.append(text)
                except:
                    pass
            break
    except:
        continue

if messages:
    print(f"\n[OK] Detected {len(messages)} messages:")
    for i, msg in enumerate(messages[-5:], 1):
        preview = msg[:50] + "..." if len(msg) > 50 else msg
        print(f"    {i}. {preview}")
    
    # Auto-reply
    print("\n[6] Sending auto-reply...")
    
    reply = "Thanks for your message! 🤖 Humara team jald reply karega."
    
    input_selectors = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][role="textbox"]',
        'footer div[contenteditable="true"]',
        'div[role="textbox"]',
    ]
    
    input_box = None
    for selector in input_selectors:
        try:
            input_box = page.query_selector(selector)
            if input_box:
                print(f"[OK] Input found: {selector}")
                break
        except:
            continue
    
    if input_box:
        try:
            input_box.fill(reply)
            time.sleep(0.5)
            page.keyboard.press("Enter")
            time.sleep(1)
            print("[OK] Reply sent!")
            page.screenshot(path="whatsapp_reply_sent.png")
        except Exception as e:
            print(f"[!] Send failed: {e}")
    else:
        print("[!] Message input not found!")
        print("    Make sure a chat is open")
else:
    print("[!] No messages detected!")
    print("    Make sure you have opened a chat with messages")

print("\n[*] Browser open for 30 seconds to verify...")
time.sleep(30)

browser.close()
playwright.stop()

print("\n[OK] Done!")
