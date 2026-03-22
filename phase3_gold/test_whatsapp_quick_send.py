"""
WhatsApp Web - Quick Send Test
Sends test message to hardcoded number
"""
from playwright.sync_api import sync_playwright

# EDIT THESE
RECIPIENT = "923182383594"  # Change to your test number
MESSAGE = "Hello from AI Employee! WhatsApp test successful"

print("=" * 60)
print("WhatsApp Web - Quick Send Test")
print("=" * 60)
print("\n[*] Testing WhatsApp message send...")
print(f"[*] Recipient: {RECIPIENT}")
print(f"[*] Message: {MESSAGE}")

playwright = sync_playwright().start()

print("\n[1] Launching browser with saved session...")
browser = playwright.chromium.launch_persistent_context(
    user_data_dir="./whatsapp_session",
    headless=False,
    args=['--disable-blink-features=AutomationControlled']
)

print("[2] Opening WhatsApp Web...")
page = browser.new_page()
page.goto("https://web.whatsapp.com/", timeout=60000)

print("[3] Waiting for login...")
page.wait_for_timeout(10000)

# Check login
is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
if not is_logged_in:
    print("\n[!] Not logged in! Waiting 30 more seconds...")
    page.wait_for_timeout(30000)
    is_logged_in = page.query_selector('div[data-testid="default-user"]') is None
    if not is_logged_in:
        print("\n[!] Still not logged in. Exiting...")
        browser.close()
        playwright.stop()
        exit(1)

print("\n[OK] Logged in!")

# Open chat with recipient
print(f"\n[4] Opening chat with {RECIPIENT}...")
chat_url = f"https://web.whatsapp.com/send?phone={RECIPIENT}"
page.goto(chat_url, timeout=60000)

print("[5] Waiting for chat to load...")
page.wait_for_timeout(10000)

# Take screenshot
page.screenshot(path="whatsapp_before_send.png")
print("[*] Screenshot saved: whatsapp_before_send.png")

# Find and use message input
print("\n[6] Finding message input...")

input_box = page.query_selector('div[contenteditable="true"][data-tab="10"]')

if input_box:
    print("[OK] Input box found!")
    
    # Type message
    print(f"[7] Typing: {MESSAGE}")
    input_box.fill(MESSAGE)
    page.wait_for_timeout(500)
    
    # Send
    print("[8] Pressing Enter to send...")
    page.keyboard.press("Enter")
    page.wait_for_timeout(2000)
    
    print("\n[OK] Message sent!")
    
    # Screenshot after
    page.screenshot(path="whatsapp_after_send.png")
    print("[*] Screenshot saved: whatsapp_after_send.png")
else:
    print("\n[!] Input box not found!")
    print("    - Recipient may not exist on WhatsApp")
    print("    - Chat may not be loaded properly")
    print("    - Check the screenshot: whatsapp_before_send.png")

print("\n[*] Browser open for 15 seconds to verify...")
page.wait_for_timeout(15000)

browser.close()
playwright.stop()

print("\n[OK] Done!")
