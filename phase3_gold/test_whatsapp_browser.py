"""
Quick WhatsApp Test - Check if browser launches
"""
import os
import sys
from playwright.sync_api import sync_playwright

print("=" * 60)
print("WhatsApp Browser Test")
print("=" * 60)

print("\n[1] Launching Playwright...")
playwright = sync_playwright().start()

print("[2] Launching Chromium browser...")
browser = playwright.chromium.launch(
    headless=False,  # Show browser
    args=[
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--start-maximized'
    ]
)

print("[3] Opening WhatsApp Web...")
page = browser.new_page()
page.goto("https://web.whatsapp.com/", timeout=60000)

print("[4] Waiting for page to load...")
page.wait_for_timeout(10000)

print("\n[OK] Browser launched!")
print("[OK] WhatsApp Web is open!")
print("\nNOW SCAN QR CODE WITH YOUR PHONE:")
print("   WhatsApp - Settings - Linked Devices - Link a Device")
print("\nWaiting 60 seconds for QR scan...")

try:
    # Wait for chat list (means QR was scanned)
    page.wait_for_selector('div[role="navigation"]', timeout=60000)
    print("\n[OK] QR SCANNED SUCCESSFULLY!")
except:
    print("\n[TIMEOUT] 60 seconds timeout - QR not scanned yet")

print("\n[5] Closing browser...")
browser.close()
playwright.stop()

print("\n✅ Test complete!")
