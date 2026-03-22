#!/usr/bin/env python3
"""
WhatsApp - Working Auto Reply Test
Fixed version with correct selectors
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "whatsapp_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("📱 WhatsApp - Auto Reply Test")
print("=" * 60)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,
        timeout=30000,
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")
    
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. Manually open ANY chat")
    print("2. Send: hello, price, order, delivery")
    print("3. Auto-reply will be sent!")
    print("=" * 60)
    print("\n⏳ 15 seconds to open a chat...")
    time.sleep(15)
    
    # Get chat name
    try:
        chat_name = page.locator('div[data-testid="chat-info-name"]').first.inner_text(timeout=3000)
        print(f"✅ Current chat: {chat_name}")
    except:
        print("⚠️  Could not detect chat name")
        chat_name = "Unknown"
    
    print("\n👀 Monitoring messages (90 seconds)...\n")
    
    seen_messages = set()
    last_reply_time = 0  # Track last reply time
    
    for i in range(90):
        try:
            # Use working selector: div.message-in
            msg_elements = page.locator('div.message-in').all()
            
            if msg_elements:
                # Get last message
                latest = msg_elements[-1]
                try:
                    msg_text = latest.inner_text(timeout=500).strip()
                except:
                    continue
                
                msg_id = f"msg_{hash(msg_text)}"
                
                # Check if new message
                if msg_text and msg_id not in seen_messages:
                    seen_messages.add(msg_id)
                    print(f"[{i}s] 📨 New: {msg_text}")

                    # Rate limit: 5 seconds between replies
                    current_time = time.time()
                    if current_time - last_reply_time < 5:
                        print("   (Rate limit - waiting 5s)")
                        continue

                    # Find keyword and reply
                    msg_lower = msg_text.lower()
                    reply = None
                    
                    if 'hello' in msg_lower or 'hi' in msg_lower:
                        reply = "Hello! How can we help you today? 👋"
                    elif 'price' in msg_lower or 'cost' in msg_lower:
                        reply = "Our products are in the $10-$50 range. 📦"
                    elif 'order' in msg_lower or 'book' in msg_lower:
                        reply = "For order please send address and product name. 📝"
                    elif 'delivery' in msg_lower or 'shipping' in msg_lower:
                        reply = "Delivery 3-5 days mein hoti hai. 🚚"
                    elif 'contact' in msg_lower or 'phone' in msg_lower:
                        reply = "Contact: 0300-1234567 📞"
                    else:
                        reply = "Thanks! 🤖 Our team will place the order soon."
                    
                    if reply:
                        print(f"   🤖 Reply: {reply}")
                        
                        # Send reply
                        try:
                            # Try different input selectors
                            input_selectors = [
                                'div[contenteditable="true"][data-tab="10"]',
                                'div[contenteditable="true"]',
                                'footer div[contenteditable="true"]',
                            ]
                            
                            for sel in input_selectors:
                                try:
                                    input_box = page.locator(sel).first
                                    if input_box.is_visible(timeout=1000):
                                        input_box.fill(reply)
                                        time.sleep(0.3)
                                        input_box.press('Enter')
                                        print(f"   ✅ SENT!")
                                        last_reply_time = time.time()  # Update reply time
                                        break
                                except:
                                    continue
                        except Exception as e:
                            print(f"   ❌ Send error: {e}")
                            
        except Exception as e:
            pass
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
    time.sleep(20)
    context.close()
