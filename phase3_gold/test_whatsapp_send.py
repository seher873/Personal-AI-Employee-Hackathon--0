"""
WhatsApp Web - Send Message via Browser
Test sending message through WhatsApp Web
"""
from playwright.sync_api import sync_playwright
import sys

print("=" * 60)
print("WhatsApp Web - Send Message Test")
print("=" * 60)

# Get recipient number
recipient = input("\nEnter recipient number (with country code, e.g., 923283490851): ").strip()
if not recipient:
    print("[!] No number entered. Exiting...")
    sys.exit(1)

message = input("Enter message to send: ").strip()
if not message:
    print("[!] No message entered. Exiting...")
    sys.exit(1)

print(f"\n[*] Will send to: {recipient}")
print(f"[*] Message: {message}")

playwright = sync_playwright().start()

print("\n[1] Launching browser...")
browser = playwright.chromium.launch_persistent_context(
    user_data_dir="./whatsapp_session",
    headless=False,
    args=['--disable-blink-features=AutomationControlled']
)

print("[2] Opening WhatsApp Web...")
page = browser.new_page()
page.goto("https://web.whatsapp.com/", timeout=60000)

print("[3] Waiting for login...")
page.wait_for_timeout(15000)

# Check if logged in
is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
if not is_logged_in:
    print("\n[!] NOT LOGGED IN!")
    print("    Please scan QR code...")
    page.wait_for_timeout(30000)
    is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
    if not is_logged_in:
        print("\n[!] Still not logged in. Exiting...")
        browser.close()
        playwright.stop()
        sys.exit(1)

print("\n[OK] Logged in!")

# Method 1: Open direct chat URL
print(f"\n[4] Opening chat with {recipient}...")
chat_url = f"https://web.whatsapp.com/send?phone={recipient}"
page.goto(chat_url, timeout=60000)

print("[5] Waiting for chat to load (15 seconds)...")
page.wait_for_timeout(15000)

# Take screenshot
print("[*] Taking screenshot...")
page.screenshot(path="whatsapp_send_test.png")
print("    Saved: whatsapp_send_test.png")

# Try to find message input box
print("\n[6] Looking for message input box...")

# Click on message input
input_found = False
for selector in [
    'div[contenteditable="true"][data-tab="10"]',
    'div[contenteditable="true"]',
    'footer div[contenteditable="true"]',
]:
    input_box = page.query_selector(selector)
    if input_box:
        print(f"[OK] Found input box with: {selector}")
        input_found = True
        
        # Type message
        print(f"[7] Typing message: {message[:30]}...")
        input_box.fill(message)
        page.wait_for_timeout(1000)
        
        # Press Enter to send
        print("[8] Sending message...")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        
        print("\n[OK] Message sent!")
        break

if not input_found:
    print("\n[!] Message input box not found!")
    print("    Make sure the chat is open and recipient exists on WhatsApp")

print("\n[*] Browser will stay open for 20 seconds to verify...")
page.wait_for_timeout(20000)

browser.close()
playwright.stop()

print("\n[OK] Done!")
