#!/usr/bin/env python3
"""
WhatsApp - Send to Seher Khan (Manual Confirm)
Opens chat and waits for you to confirm before sending
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "whatsapp_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMER = "Seher khan"

PRODUCT_MESSAGE = """🎉 SPECIAL OFFER! 🎉

Premium Quality Products at Best Prices!

👕 Shirts - Rs. 2500 only
👟 Shoes - Rs. 3500 only
⌚ Watches - Rs. 5000 only

📦 Order Now!
💰 Cash on Delivery
🚚 3-5 Days Delivery"""

print("=" * 60)
print("📱 WhatsApp - Send to Seher Khan")
print("=" * 60)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,
        timeout=30000,
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")
    
    print("\n📲 Loading WhatsApp...")
    time.sleep(5)
    
    # Login check
    print("🔐 Login check...")
    for i in range(10):
        try:
            if page.locator('div[data-testid="chat-list"]').first.is_visible(timeout=2000):
                print("✅ Logged in!")
                break
        except:
            print(f"⏳ Waiting... ({(i+1)*2}s)")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("MANUAL STEPS:")
    print("=" * 60)
    print("1. Search 'Seher khan' in search box")
    print("2. Click on the correct chat")
    print("3. Make sure chat is open")
    print("4. Script will send message after 30 seconds")
    print("=" * 60)
    
    print("\n⏳ 30 seconds to open chat manually...")
    for i in range(30, 0, -1):
        print(f"   {i}s remaining...")
        time.sleep(1)
    
    print("\n📝 Sending message in 5 seconds...")
    print("   Make sure Seher Khan's chat is open!")
    time.sleep(5)
    
    # Verify chat is open
    try:
        chat_header = page.locator('div[data-testid="chat-info-name"]').first.inner_text(timeout=3000)
        print(f"✅ Current chat: {chat_header}")
    except:
        print("⚠️  Could not detect chat - continuing anyway")
    
    # Send message
    print("\n🚀 Sending product message...")
    
    input_selectors = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][data-tab="60"]',
        'footer div[contenteditable="true"]',
        'div[role="textbox"]',
    ]
    
    sent = False
    for sel in input_selectors:
        try:
            input_box = page.locator(sel).first
            if input_box.is_visible(timeout=2000):
                print(f"   Found input box: {sel}")
                input_box.fill(PRODUCT_MESSAGE)
                time.sleep(1)
                input_box.press('Enter')
                time.sleep(1)
                input_box.press('Enter')  # Extra enter to ensure send
                print("   ✅ MESSAGE SENT!")
                sent = True
                
                # Screenshot
                screenshot_dir = BASE_DIR / "Screenshots"
                screenshot_dir.mkdir(exist_ok=True)
                page.screenshot(path=str(screenshot_dir / "sent_seher_confirm.png"))
                print("   📸 Screenshot saved!")
                break
        except Exception as e:
            print(f"   Trying next selector... ({e})")
            continue
    
    if not sent:
        print("\n❌ Could not send automatically!")
        print("   Please copy this message and send manually:")
        print("-" * 40)
        print(PRODUCT_MESSAGE)
        print("-" * 40)
        time.sleep(30)
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)
    time.sleep(20)
    context.close()
