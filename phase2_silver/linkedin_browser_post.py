#!/usr/bin/env python3
"""
LinkedIn Browser Poster - Post using browser automation
No API required - uses LinkedIn credentials directly
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

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "linkedin_credentials.json"

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
    
    # Keep browser open for debugging
    chrome_options.add_experimental_option("detach", True)
    
    try:
        # Use webdriver-manager to auto-install ChromeDriver
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        return driver
    except Exception as e:
        print(f"❌ ChromeDriver error: {e}")
        print("\n💡 Make sure Google Chrome is installed")
        return None

def login_linkedin(driver, email, password):
    """Login to LinkedIn"""
    print("🔐 Logging in to LinkedIn...")
    
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)  # Wait longer for page to load
    
    try:
        # Enter email - try multiple selectors
        email_field = None
        selectors = [
            ("ID", "username"),
            ("ID", "session_key"),
            ("NAME", "session_key"),
            ("CSS", "input[type='email']"),
            ("CSS", "input[id*='username']"),
            ("CSS", "input[name*='username']"),
            ("XPATH", "//input[@type='email' or @type='text']"),
        ]
        
        for by, value in selectors:
            try:
                if by == "ID":
                    email_field = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.ID, value))
                    )
                elif by == "NAME":
                    email_field = driver.find_element(By.NAME, value)
                elif by == "CSS":
                    email_field = driver.find_element(By.CSS_SELECTOR, value)
                elif by == "XPATH":
                    email_field = driver.find_element(By.XPATH, value)
                    
                if email_field:
                    print(f"✅ Email field found using: {by}={value}")
                    break
            except:
                continue
        
        if not email_field:
            print("❌ Email field not found")
            print(f"   Current URL: {driver.current_url}")
            print(f"   Page title: {driver.title}")
            # Save page source for debugging
            with open("login_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("   Saved page source to login_page.html")
            return False
            
        email_field.clear()
        email_field.send_keys(email)
        
        # Enter password
        password_field = None
        for selector in ["#password", "#session_password", "input[name='session_password']", "input[type='password']"]:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Password field found: {selector}")
                break
            except:
                continue
        
        if not password_field:
            print("❌ Password field not found")
            return False
            
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Click sign in button
        sign_in_button = None
        for selector in ["button[type='submit']", "input[type='submit']", "button[data-litms-control*='submit']"]:
            try:
                sign_in_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if sign_in_button:
            sign_in_button.click()
        else:
            password_field.send_keys(Keys.RETURN)
        
        # Wait for login
        time.sleep(5)
        
        # Check if login successful
        if "feed" in driver.current_url or "mynetwork" in driver.current_url or "/feed/" in driver.current_url:
            print("✅ Login successful!")
            return True
        elif "checkpoint" in driver.current_url:
            print("⚠️  LinkedIn security checkpoint detected. Please verify manually.")
            return False
        else:
            print("❌ Login failed. Please check credentials.")
            print(f"   Current URL: {driver.current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def create_post(driver, text):
    """Create a post on LinkedIn"""
    print("📝 Creating post...")
    
    try:
        # Go to LinkedIn homepage
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        
        # Try to find and click the post creation box
        post_box_clicked = False
        
        # Method 1: Click on "Start a post"
        try:
            post_box = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Start a post') or contains(., 'Post')]")
                )
            )
            driver.execute_script("arguments[0].click();", post_box)
            post_box_clicked = True
            print("✅ Post box clicked (Method 1)")
        except Exception as e1:
            # Method 2: Click on the share box
            try:
                post_box = driver.find_element(By.CSS_SELECTOR, "div.share-box-feed-entry")
                driver.execute_script("arguments[0].click();", post_box)
                post_box_clicked = True
                print("✅ Post box clicked (Method 2)")
            except Exception as e2:
                print(f"⚠️  Could not click post box: {e1}")
        
        time.sleep(3)
        
        # Find the textarea and enter text
        try:
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true']")
                )
            )
            
            # Use JavaScript to set text (handles emojis better)
            driver.execute_script("arguments[0].textContent = arguments[1];", textarea, text)
            print(f"✅ Text entered: {text[:50]}...")
            
            time.sleep(2)
            
            # Find and click Post button
            try:
                post_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'share-actions__post-button') or contains(@class, 'post-button')]")
                    )
                )
                
                print("✅ Post button found, clicking...")
                driver.execute_script("arguments[0].click();", post_button)
                
                time.sleep(3)
                print("✅ Post published successfully!")
                return True
                
            except Exception as e:
                print(f"⚠️  Could not click post button: {e}")
                print("💡 Browser window is open - you can manually click Post")
                return True  # Text is entered, user can manually post
                
        except Exception as e:
            print(f"❌ Could not find text area: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating post: {e}")
        print("\n💡 Browser window is open - you can post manually")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("💼 LinkedIn Browser Poster")
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
    if not driver:
        return 1
    
    try:
        # Login
        if not login_linkedin(driver, email, password):
            print("\n❌ Login failed. Check credentials in linkedin_credentials.json")
            return 1
        
        time.sleep(2)
        
        # Create post
        create_post(driver, args.text)
        
        print("\n" + "=" * 60)
        print("✅ Done! Browser will stay open for 30 seconds...")
        print("=" * 60)
        
        time.sleep(30)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        # Don't close browser automatically
        # driver.quit()
        pass

if __name__ == '__main__':
    sys.exit(main())
