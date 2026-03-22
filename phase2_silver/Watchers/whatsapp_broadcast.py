#!/usr/bin/env python3
"""
WhatsApp - Product Broadcast to Customers
Send product info to multiple customers automatically
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "whatsapp_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# CUSTOMER LIST - Add your customers here
# ============================================
CUSTOMERS = [
    "Ali Khan",
    "Ahmed",
    "Seher khan",
]

# ============================================
# PRODUCT MESSAGE - Edit your product info here
# ============================================
PRODUCT_MESSAGE = """
🎉 SPECIAL OFFER! 🎉

Premium Quality Products at Best Prices!

👕 Shirts - Rs. 2500 only
   Sizes: M, L, XL
   Colors: Black, White, Blue

👟 Shoes - Rs. 3500 only
   Sizes: 40-44
   Free Delivery!

⌚ Watches - Rs. 5000 only
   1 Year Warranty

📦 Order Now!
💰 Cash on Delivery Available
🚚 Delivery: 3-5 Days

Reply for more details! 📞
"""

# ============================================
# SETTINGS
# ============================================
DELAY_BETWEEN_MESSAGES = 10  # Seconds between each customer
DELAY_AFTER_OPEN = 3  # Seconds to wait after opening chat

print("=" * 60)
print("📱 WhatsApp - Product Broadcast")
print("=" * 60)

print(f"\n📋 Customers: {len(CUSTOMERS)}")
for c in CUSTOMERS[:5]:
    print(f"   - {c}")
if len(CUSTOMERS) > 5:
    print(f"   ... and {len(CUSTOMERS)-5} more")

print(f"\n⏱️  Delay between messages: {DELAY_BETWEEN_MESSAGES}s")
print(f"\n📦 Product Message:")
print("-" * 40)
print(PRODUCT_MESSAGE[:100] + "...")
print("-" * 40)

print("\n" + "=" * 60)
print("INSTRUCTIONS:")
print("=" * 60)
print("1. Browser will open WhatsApp Web")
print("2. Script will search each customer and send message")
print("3. You can watch it working in real-time")
print("=" * 60)
print("\n🚀 Starting in 5 seconds...")
time.sleep(5)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,  # VISIBLE browser
        timeout=30000,
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")
    
    print("\n📲 Waiting for WhatsApp to load...")
    time.sleep(5)
    
    # Check login
    print("🔐 Checking login...")
    for i in range(10):
        try:
            if page.locator('div[data-testid="chat-list"]').first.is_visible(timeout=2000):
                print("✅ Logged in!")
                break
        except:
            print(f"⏳ Waiting for login... ({(i+1)*2}s)")
            time.sleep(2)
    else:
        print("⚠️  Please scan QR code manually")
        time.sleep(30)
    
    sent_count = 0
    failed_count = 0
    
    print("\n" + "=" * 60)
    print("🚀 Starting Broadcast")
    print("=" * 60)
    
    for i, customer in enumerate(CUSTOMERS, 1):
        print(f"\n[{i}/{len(CUSTOMERS)}] 📤 Sending to: {customer}")
        
        try:
            # Click on search box
            print("   🔍 Searching customer...")
            search_box = page.locator('div[contenteditable="true"][data-tab="3"]').first
            search_box.click()
            time.sleep(1)
            
            # Clear and type customer name
            search_box.press('Control+a')
            time.sleep(0.5)
            search_box.press('Backspace')
            time.sleep(0.5)
            search_box.fill(customer)
            time.sleep(2)
            
            # Click on first result
            print("   📍 Opening chat...")
            try:
                result = page.locator('div[role="listitem"]').first
                result.click(timeout=3000)
                time.sleep(DELAY_AFTER_OPEN)
            except:
                print(f"   ⚠️  Customer '{customer}' not found, skipping...")
                failed_count += 1
                time.sleep(DELAY_BETWEEN_MESSAGES)
                continue
            
            # Type and send message
            print("   📝 Sending message...")
            input_box = page.locator('div[contenteditable="true"][data-tab="10"]').first
            
            # Split message into lines and send
            for line in PRODUCT_MESSAGE.strip().split('\n'):
                if line.strip():
                    input_box.fill(line)
                    input_box.press('Enter')
                    time.sleep(0.3)
            
            # Send final newline to ensure message goes
            input_box.press('Enter')
            time.sleep(1)
            
            print(f"   ✅ SENT to {customer}!")
            sent_count += 1
            
            # Screenshot
            try:
                screenshot_dir = BASE_DIR / "Screenshots"
                screenshot_dir.mkdir(exist_ok=True)
                page.screenshot(path=str(screenshot_dir / f"broadcast_{i}.png"))
            except:
                pass
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1
        
        # Wait before next customer
        if i < len(CUSTOMERS):
            print(f"   ⏳ Waiting {DELAY_BETWEEN_MESSAGES}s before next...")
            time.sleep(DELAY_BETWEEN_MESSAGES)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BROADCAST SUMMARY")
    print("=" * 60)
    print(f"✅ Sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Total: {len(CUSTOMERS)}")
    print("=" * 60)
    
    print("\nBrowser will close in 30 seconds...")
    time.sleep(30)
    context.close()
    
    print("✅ Done!")
