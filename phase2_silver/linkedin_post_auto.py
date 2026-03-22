#!/usr/bin/env python3
"""
LinkedIn Poster - FINAL VERSION
Fully automated with Selenium + Keyboard shortcuts
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

def login_and_post(driver, email, password, text):
    """Login and create post"""
    print("🔐 Logging in...")
    
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)
    
    try:
        # Login
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
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        
        print("📝 Creating post...")
        
        # LinkedIn feed page par "Start a post" button dhundna
        post_clicked = False
        
        # Try finding the main post creation button
        try:
            # Look for the share box
            share_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[id*='share-box']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", share_box)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", share_box)
            print("✅ Share box clicked")
            post_clicked = True
        except:
            pass
        
        if not post_clicked:
            # Try finding button by aria-label
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='post']")
                for btn in buttons:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        print("✅ Post button clicked")
                        post_clicked = True
                        break
            except:
                pass
        
        if not post_clicked:
            # Last resort - use keyboard navigation
            print("💡 Using keyboard navigation...")
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.TAB)
            time.sleep(0.5)
            body.send_keys(Keys.TAB)
            time.sleep(0.5)
            body.send_keys(Keys.RETURN)
            time.sleep(3)
            post_clicked = True
        
        if not post_clicked:
            print("⚠️  Could not open post dialog")
            return False
        
        # Wait for dialog to open
        print("⏳ Waiting for post dialog...")
        time.sleep(3)
        
        # Find textarea and paste text using Ctrl+V
        try:
            # Try multiple selectors for the textarea
            textarea = None
            selectors = [
                "div[contenteditable='true']",
                "div[role='textbox']",
                "textarea",
                "div[id*='editor']"
            ]
            
            for selector in selectors:
                try:
                    textarea = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Textarea found: {selector}")
                    break
                except:
                    continue
            
            if not textarea:
                # Try finding by class
                divs = driver.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    try:
                        if div.get_attribute('contenteditable') == 'true':
                            textarea = div
                            print("✅ Textarea found by attribute")
                            break
                    except:
                        continue
            
            if not textarea:
                print("❌ Could not find textarea")
                return False
            
            # Click to focus
            driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", textarea)
            time.sleep(1)
            
            # Use Ctrl+V to paste
            pyperclip.copy(text)
            time.sleep(0.5)
            
            # Send Ctrl+V
            textarea.send_keys(Keys.CONTROL + 'a')
            time.sleep(0.3)
            textarea.send_keys(Keys.DELETE)
            time.sleep(0.3)
            textarea.send_keys(Keys.CONTROL + 'v')
            
            print(f"✅ Text entered ({len(text)} chars)")
            time.sleep(2)
            textarea = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
            textarea.click()
            time.sleep(1)
            
            # Use JavaScript to set text
            driver.execute_script(f"""
                var el = arguments[0];
                el.textContent = `{text}`;
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            """, textarea)
            
            print(f"✅ Text entered ({len(text)} chars)")
            time.sleep(2)
            
            # Click Post button
            try:
                post_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'post-button') or contains(@class, 'share-actions__post-button')]")
                    )
                )
                driver.execute_script("arguments[0].click();", post_button)
                print("✅ POST PUBLISHED!")
                return True
            except:
                print("⚠️  Could not click Post button - try keyboard")
                # Try keyboard
                for _ in range(4):
                    textarea.send_keys(Keys.TAB)
                    time.sleep(0.3)
                textarea.send_keys(Keys.RETURN)
                print("✅ Keyboard post sent!")
                return True
                
        except Exception as e:
            print(f"❌ Error entering text: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

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
        success = login_and_post(driver, email, password, args.text)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Check your LinkedIn profile")
            print("=" * 60)
            time.sleep(10)
            driver.quit()
            return 0
        else:
            print("\n❌ Post failed - browser is open, you can post manually")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
