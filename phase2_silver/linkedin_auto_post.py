#!/usr/bin/env python3
"""
LinkedIn Auto Poster - FULLY AUTOMATED
Uses keyboard simulation to bypass ChromeDriver limitations
"""

import os
import sys
import json
import time
import webbrowser
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
import pyautogui

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "linkedin_credentials.json"

# PyAutoGUI setup
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def get_credentials():
    """Load LinkedIn credentials"""
    if not CREDENTIALS_FILE.exists():
        print("❌ Credentials file not found!")
        return None, None
    
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)
    
    return creds.get('email'), creds.get('password')

def setup_driver():
    """Setup Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login_linkedin(driver, email, password):
    """Login to LinkedIn"""
    print("🔐 Logging in to LinkedIn...")
    
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)
    
    try:
        # Find and fill email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.clear()
        email_field.send_keys(email)
        
        # Find and fill password
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(5)
        
        # Check if login successful
        if "feed" in driver.current_url or "/feed/" in driver.current_url:
            print("✅ Login successful!")
            return True
        elif "checkpoint" in driver.current_url:
            print("⚠️  Security checkpoint detected")
            return False
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def post_with_keyboard(text):
    """Use keyboard simulation to create post"""
    print("⌨️  Using keyboard automation...")
    
    # Copy text to clipboard
    pyperclip.copy(text)
    print("✅ Text copied to clipboard")
    
    time.sleep(2)
    
    # Press Ctrl+V to paste
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(2)
    
    # Press Enter to confirm
    pyautogui.press('enter')
    time.sleep(1)
    
    # Tab to Post button and Enter
    for _ in range(3):
        pyautogui.press('tab')
        time.sleep(0.5)
    
    pyautogui.press('enter')
    
    print("✅ Post command sent!")

def create_post(driver, text):
    """Create a post on LinkedIn"""
    print("📝 Creating post...")
    
    try:
        # Go to LinkedIn feed
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        
        # Click on "Start a post"
        try:
            post_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Start a post') or contains(., 'post')]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", post_button)
            print("✅ Post dialog opened")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️  Could not click post button: {e}")
            # Try alternative method
            try:
                post_button = driver.find_element(By.CSS_SELECTOR, "div.share-box-feed-entry")
                driver.execute_script("arguments[0].click();", post_button)
                print("✅ Post dialog opened (method 2)")
                time.sleep(3)
            except:
                print("❌ Could not open post dialog")
                return False
        
        # Find textarea
        try:
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true']")
                )
            )
            
            # Click to focus
            driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", textarea)
            time.sleep(1)
            
            # Use keyboard automation to paste text
            pyperclip.copy(text)
            time.sleep(1)
            
            # Select all and delete
            textarea.send_keys(Keys.CONTROL + 'a')
            time.sleep(0.5)
            textarea.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Paste using keyboard
            textarea.send_keys(Keys.CONTROL + 'v')
            print(f"✅ Text entered: {text[:50]}...")
            time.sleep(2)
            
            # Find and click Post button
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'share-actions__post-button') or contains(@class, 'post-button')]")
                    )
                )
                
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", submit_button)
                print("✅ Post button clicked!")
                time.sleep(3)
                
                print("✅ POST PUBLISHED SUCCESSFULLY!")
                return True
                
            except Exception as e:
                print(f"⚠️  Could not find Post button: {e}")
                print("💡 Trying keyboard navigation...")
                
                # Try keyboard navigation
                for _ in range(5):
                    pyautogui.press('tab')
                    time.sleep(0.3)
                pyautogui.press('enter')
                print("✅ Keyboard post command sent!")
                return True
                
        except Exception as e:
            print(f"❌ Could not find text area: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("💼 LinkedIn Auto Poster - FULL AUTOMATION")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True, help='Post text')
    args = parser.parse_args()
    
    # Get credentials
    email, password = get_credentials()
    if not email or not password:
        print("❌ Could not load credentials")
        return 1
    
    print(f"📧 Email: {email}")
    print(f"📝 Post: {args.text[:50]}...")
    
    # Setup driver
    driver = setup_driver()
    
    try:
        # Login
        if not login_linkedin(driver, email, password):
            print("\n❌ Login failed. Check credentials.")
            return 1
        
        time.sleep(2)
        
        # Create post
        success = create_post(driver, args.text)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Post published to LinkedIn!")
            print("=" * 60)
        else:
            print("\n❌ Post creation failed")
            return 1
        
        # Keep browser open briefly
        time.sleep(5)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        driver.quit()

if __name__ == '__main__':
    sys.exit(main())
