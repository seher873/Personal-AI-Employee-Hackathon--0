#!/usr/bin/env python3
"""
LinkedIn Automation Script
Automatically creates and posts content to your LinkedIn profile.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInAutomation:
    """
    Automated LinkedIn posting and monitoring.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.content_dir = os.path.join(vault_path, "Content")
        self.posted_dir = os.path.join(vault_path, "Posted")
        self.logs_dir = os.path.join(vault_path, "Logs")
        self.driver = None

        # Ensure directories exist
        for directory in [self.content_dir, self.posted_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

        # LinkedIn credentials (will be loaded from file)
        self.credentials = self.load_credentials()

    def load_credentials(self):
        """Load LinkedIn credentials from file."""
        creds_file = os.path.join(self.vault_path, "linkedin_credentials.json")
        if os.path.exists(creds_file):
            with open(creds_file, 'r') as f:
                return json.load(f)
        else:
            # Create template
            template = {
                "email": "",
                "password": "",
                "profile_url": ""
            }
            with open(creds_file, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"Created template credentials file: {creds_file}")
            logger.info("Please fill in your LinkedIn credentials")
            return None

    def setup_driver(self):
        """Setup Chrome driver for LinkedIn automation."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Create a temporary profile to avoid conflicts
        import tempfile
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument("--profile-directory=Default")

        # Add user agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info("Chrome driver initialized")

    def login_to_linkedin(self):
        """Login to LinkedIn."""
        if not self.credentials or not self.credentials.get("email"):
            logger.error("LinkedIn credentials not configured")
            return False

        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            # Check if already logged in
            if "feed" in self.driver.current_url:
                logger.info("Already logged in to LinkedIn")
                return True

            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.credentials["email"])

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.credentials["password"])

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            time.sleep(5)

            # Check if login successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                logger.error("LinkedIn login failed")
                return False

        except Exception as e:
            logger.error(f"Error during LinkedIn login: {e}")
            return False

    def generate_post_content(self, topic="business automation"):
        """Generate engaging LinkedIn post content."""

        # Always use the user's exact topic as the post content
        return {
            "hook": topic[:100] + "..." if len(topic) > 100 else topic,
            "body": topic,
            "hashtags": "#LinkedIn #Post #Update #Business #AI #Automation"
        }

    def create_post_on_linkedin(self, content):
        """Create a post on LinkedIn."""
        try:
            # Navigate to LinkedIn feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(5)

            # Try multiple selectors for the post button
            post_button_selectors = [
                "//button[contains(@class, 'share-box-feed-entry__trigger')]",
                "//button[contains(@aria-label, 'Create a post')]",
                "//div[contains(@class, 'share-box-feed-entry')]//button",
                "button[aria-label*='Create a post']",
                "button[data-control-name='share.post']"
            ]

            post_button = None
            for selector in post_button_selectors:
                try:
                    if selector.startswith("//"):
                        post_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        post_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue

            if not post_button:
                logger.error("Could not find post button")
                return False

            post_button.click()
            time.sleep(3)

            # Find text area - try multiple selectors
            text_area_selectors = [
                "//div[@contenteditable='true' and @role='textbox']",
                "//div[@data-placeholder='What do you want to talk about?']",
                "div[contenteditable='true']",
                "[data-placeholder*='talk about']"
            ]

            text_area = None
            for selector in text_area_selectors:
                try:
                    if selector.startswith("//"):
                        text_area = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        text_area = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue

            if not text_area:
                logger.error("Could not find text area")
                return False

            # Clear and enter content
            text_area.click()
            time.sleep(1)

            # Build content
            full_content = f"{content['hook']}\n\n{content['body']}\n\n{content['hashtags']}\n\n#AIEmployee #BusinessAutomation #Consulting"

            # Type content character by character for better reliability
            for char in full_content:
                text_area.send_keys(char)
                time.sleep(0.01)

            time.sleep(3)

            # Find and click post button
            post_submit_selectors = [
                "//button[contains(@class, 'share-actions__primary-action')]",
                "//button[contains(@aria-label, 'Post')]",
                "button[data-control-name='share.post']",
                "button[aria-label*='Post']"
            ]

            post_submit = None
            for selector in post_submit_selectors:
                try:
                    if selector.startswith("//"):
                        post_submit = self.driver.find_element(By.XPATH, selector)
                    else:
                        post_submit = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if post_submit and post_submit.is_enabled():
                        break
                except:
                    continue

            if not post_submit:
                logger.error("Could not find post submit button")
                return False

            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_submit)
            time.sleep(1)
            post_submit.click()

            # Wait for post to complete
            time.sleep(10)

            # Check if post was successful
            current_url = self.driver.current_url
            if "feed" in current_url:
                logger.info("Successfully posted to LinkedIn")
                return True
            else:
                logger.warning("Post may not have completed successfully")
                return False

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            self.driver.save_screenshot(f"linkedin_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            return False

    def post_to_linkedin(self, topic="AI automation benefits"):
        """Main method to post to LinkedIn."""
        try:
            self.setup_driver()

            if not self.login_to_linkedin():
                return False

            # Generate content
            content = self.generate_post_content(topic)

            # Save content for record
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_file = os.path.join(self.content_dir, f"linkedin_post_{timestamp}.json")
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)

            # Post to LinkedIn
            success = self.create_post_on_linkedin(content)

            if success:
                # Save posted content
                posted_file = os.path.join(self.posted_dir, f"posted_{timestamp}.json")
                with open(posted_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "content": content,
                        "posted_at": datetime.now().isoformat(),
                        "topic": topic
                    }, f, indent=2)

                logger.info(f"LinkedIn post created and saved: {posted_file}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error in LinkedIn automation: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def run_automated_posting(self, interval_hours=24):
        """Run automated LinkedIn posting on schedule."""
        logger.info(f"Starting automated LinkedIn posting (interval: {interval_hours} hours)")

        while True:
            try:
                # Generate and post content
                success = self.post_to_linkedin()

                if success:
                    logger.info(f"Posted successfully. Next post in {interval_hours} hours")
                else:
                    logger.error("Failed to post. Will retry in 1 hour")
                    time.sleep(3600)
                    continue

                # Wait for next post
                time.sleep(interval_hours * 3600)

            except KeyboardInterrupt:
                logger.info("Automated posting stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in automated posting: {e}")
                time.sleep(3600)

def main():
    """Main function for standalone LinkedIn automation."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Automation Tool")
    parser.add_argument("--vault", default="./", help="Vault directory path")
    parser.add_argument("--post", help="Post to LinkedIn with custom topic")
    parser.add_argument("--schedule", type=int, help="Run scheduled posting every N hours")
    parser.add_argument("--test", action="store_true", help="Test without actually posting")

    args = parser.parse_args()

    automation = LinkedInAutomation(vault_path=args.vault)

    if args.post:
        # Single post
        success = automation.post_to_linkedin(args.post)
        if success:
            print("[OK] Successfully posted to LinkedIn!")
        else:
            print("[ERROR] Failed to post to LinkedIn")
    elif args.schedule:
        # Scheduled posting
        automation.run_automated_posting(args.schedule)
    elif args.test:
        # Test mode - generate content only
        content = automation.generate_post_content("AI automation")
        print("Generated content:")
        print(f"Hook: {content['hook']}")
        print(f"Body: {content['body'][:100]}...")
        print(f"Hashtags: {content['hashtags']}")
    else:
        # Default: post with AI automation topic
        success = automation.post_to_linkedin("AI automation benefits")
        if success:
            print("[OK] Successfully posted to LinkedIn!")
        else:
            print("[ERROR] Failed to post to LinkedIn")

if __name__ == "__main__":
    main()
