#!/usr/bin/env python3
"""Simple browser test"""

from playwright.sync_api import sync_playwright
import time

print("Browser open kar raha hai...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://web.whatsapp.com")
    print("✅ Browser open ho gaya!")
    print("QR code dikhai de raha hai?")
    time.sleep(120)  # 2 minutes wait
    browser.close()
    print("Done!")
