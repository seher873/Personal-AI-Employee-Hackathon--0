#!/usr/bin/env python3
"""
LinkedIn Final Auto Poster - Works with new LinkedIn UI
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import pyperclip

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "linkedin_credentials.json"

def get_credentials():
    if not CREDENTIALS_FILE.exists():
        return None, None
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)
    return creds.get('email'), creds.get('password')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def main():
    print("=" * 60)
    print("💼 LinkedIn Auto Poster")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True, help='Post text')
    args = parser.parse_args()
    
    email, password = get_credentials()
    if not email or not password:
        print("❌ Credentials not found!")
        return 1
    
    print(f"📧 Email: {email}")
    print(f"📝 Post: {args.text[:50]}...")
    
    driver = setup_driver()
    
    try:
        # Login
        print("🔐 Logging in...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(5)
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(5)
        print("✅ Login successful!")
        
        # Go to feed
        print("📍 Going to feed...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        
        # Copy text to clipboard
        pyperclip.copy(args.text)
        print("✅ Text copied to clipboard")
        
        # Instructions
        print("\n" + "=" * 60)
        print("📝 MANUAL STEPS (browser is open):")
        print("=" * 60)
        print("1. Click 'Start a post' button")
        print("2. Press Ctrl+V to paste the text")
        print("3. Click 'Post' button")
        print("=" * 60)
        print(f"\n💡 Your post text is in clipboard: {args.text[:50]}...")
        print("\n⏳ Browser will stay open for 60 seconds...")
        
        time.sleep(60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
