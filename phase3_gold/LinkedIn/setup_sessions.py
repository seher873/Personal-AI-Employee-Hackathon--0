#!/usr/bin/env python3
"""
LinkedIn Session Setup - One-time browser login to save session.
Run this once to authenticate with LinkedIn and save the session.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Configuration
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "sehrkhan873@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
USER_DATA_DIR = "./linkedin_session"

# Ensure directory exists
Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)


def setup_session():
    """Open browser for manual LinkedIn login and save session"""
    print("=" * 60)
    print("LINKEDIN SESSION SETUP")
    print("=" * 60)
    print("\n📝 INSTRUCTIONS:")
    print("1. A browser window will open")
    print("2. Navigate to linkedin.com if not already there")
    print("3. Login with your LinkedIn credentials")
    print("4. Wait until you see your feed/homepage")
    print("5. Return here and press ENTER")
    print("\n⚠️  DO NOT close the browser until you press ENTER here!")
    print("=" * 60)
    input("\nPress ENTER to open the browser...")

    try:
        with sync_playwright() as p:
            # Launch visible browser
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            context = browser.new_context()
            page = context.new_page()

            print("\n🌐 Browser opened. Logging in to LinkedIn...")
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")

            # Auto-fill if credentials available
            if LINKEDIN_EMAIL and LINKEDIN_PASSWORD:
                print("📧 Auto-filling credentials from .env...")
                try:
                    page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
                    page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
                    print("✓ Credentials filled. Please click 'Sign in' button.")
                except Exception:
                    print("⚠️  Could not auto-fill. Please login manually.")

            print("\n⏳ Waiting for you to complete login and press ENTER...")
            input("Press ENTER after you see your LinkedIn feed...")

            # Check if logged in
            current_url = page.url
            if "feed" in current_url or "mynetwork" in current_url:
                print("\n✓ Login confirmed!")

                # Save session state
                session_path = os.path.join(USER_DATA_DIR, "storage_state.json")
                context.storage_state(path=session_path)
                print(f"✓ Session saved to: {session_path}")

                print("\n" + "=" * 60)
                print("SETUP COMPLETE!")
                print("=" * 60)
                print("\nYou can now use:")
                print("  - python linkedin_watcher.py    (monitor messages)")
                print("  - python linkedin_poster.py     (create posts)")
                print("  - python linkedin_manager.py    (combined)")
                print("  - python linkedin_simple.py     (simple interface)")
                print("\n⚠️  If session expires, run this script again.")
                print("=" * 60)
            else:
                print("\n⚠️  Not on feed page. You may need to login again next time.")
                print(f"   Current URL: {current_url}")

            browser.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_session()
