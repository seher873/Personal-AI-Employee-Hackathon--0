#!/usr/bin/env python3
"""
Quick Test - Facebook Login Only
Just tests if login works (no posting)
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
from config import FB_EMAIL, FB_PASSWORD

print("=" * 60)
print("FACEBOOK LOGIN TEST")
print("=" * 60)
print(f"Email: {FB_EMAIL}")
print(f"Password: {'*' * len(FB_PASSWORD) if FB_PASSWORD else 'NOT SET'}")
print("=" * 60)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        # Navigate to Facebook
        print("Navigating to Facebook...")
        page.goto("https://www.facebook.com", timeout=60000)
        time.sleep(5)
        
        # Check if logged in
        print("Checking login status...")
        
        try:
            if page.is_visible("[data-pagelet='MainFeed']", timeout=5000):
                print("[OK] Already logged in!")
            else:
                print("[INFO] Not logged in - attempting auto-login...")
                
                # Auto-fill credentials
                if FB_EMAIL and FB_PASSWORD:
                    print("[INFO] Entering credentials...")
                    
                    # Find email field
                    try:
                        email_input = page.locator("input[type='email'], input[name='email'], #email").first
                        email_input.wait_for(state='visible', timeout=10000)
                        email_input.fill(FB_EMAIL)
                        print("[OK] Email entered")
                        time.sleep(1)
                    except Exception as e:
                        print(f"[WARN] Email input failed: {e}")
                    
                    # Find password field
                    try:
                        password_input = page.locator("input[type='password'], input[name='pass'], #pass").first
                        password_input.wait_for(state='visible', timeout=10000)
                        password_input.fill(FB_PASSWORD)
                        print("[OK] Password entered")
                        time.sleep(1)
                    except Exception as e:
                        print(f"[WARN] Password input failed: {e}")
                    
                    # Click login - try multiple selectors
                    try:
                        login_selectors = [
                            "button[type='submit']",
                            "[value*='Log In']",
                            "[value*='Log into']",
                            "button:has-text('Log in')",
                            "button:has-text('Log into')",
                            "[type='submit']",
                            "input[value*='Log']",
                        ]
                        
                        login_clicked = False
                        for selector in login_selectors:
                            try:
                                login_btn = page.locator(selector).first
                                login_btn.wait_for(state='visible', timeout=3000)
                                login_btn.click()
                                print(f"[OK] Login button clicked: {selector}")
                                login_clicked = True
                                break
                            except:
                                continue
                        
                        if not login_clicked:
                            # Fallback: Press Enter
                            print("[INFO] Using Enter key as fallback...")
                            page.keyboard.press("Enter")
                            time.sleep(5)
                            
                    except Exception as e:
                        print(f"[WARN] Login failed: {e}")
                        print("[INFO] You can manually login in the browser")
                else:
                    print("[WARN] Credentials not set in .env file")
                    print("[INFO] Please login manually in the browser")
        except Exception as e:
            print(f"[WARN] Could not determine login status: {e}")
        
        print("\nBrowser will stay open for 2 minutes...")
        print("You can manually test posting if logged in")
        print("\nIf not logged in:")
        print("1. Enter your email and password")
        print("2. Complete any 2FA if required")
        print("3. Wait for home feed to load")
        print("4. Try creating a post manually")
        time.sleep(120)  # 2 minutes
        
        browser.close()
        print("\n[OK] Test completed!")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
