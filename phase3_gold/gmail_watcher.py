"""
Gmail Watcher - Monitors Gmail for new messages
Uses Playwright for browser automation with dynamic selectors.
Saves new messages to Inbox/ directory for processing.
"""

import os
import time
import random
import json
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from selector_loader import (
    get_selector, get_selector_list, get_timeout, get_delay,
    validate_selectors
)
from config import GMAIL_EMAIL, GMAIL_PASSWORD

# =============================================================================
# CONFIGURATION - CHANGE THESE VALUES
# =============================================================================
SESSION_DIR = "./gmail_session"
STORAGE_FILE = os.path.join(SESSION_DIR, "storage_state.json")
INBOX_DIR = "./Inbox"

# Create directories if they don't exist
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(INBOX_DIR, exist_ok=True)


def human_delay(min_ms=None, max_ms=None):
    """Add human-like random delay between actions."""
    if min_ms is None:
        min_ms = get_delay("human_min")
    if max_ms is None:
        max_ms = get_delay("human_max")
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    time.sleep(delay)


def take_screenshot(page, step_name):
    """Take screenshot on error."""
    try:
        filename = f"error_{step_name}.png"
        page.screenshot(path=filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Could not take screenshot: {e}")


def save_session(context, storage_file):
    """Save session storage for auto-login."""
    try:
        storage = context.storage_state()
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        with open(storage_file, 'w') as f:
            json.dump(storage, f)
        print("Session saved")
    except Exception as e:
        print(f"Could not save session: {e}")


def load_session(storage_file):
    """Load session storage if exists."""
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def find_element_by_text(page, text_patterns, element_type="div"):
    """Find element by text patterns."""
    for pattern in text_patterns:
        try:
            elem = page.locator(f'{element_type}:has-text("{pattern}")').first
            if elem.is_visible(timeout=get_timeout("button_wait")):
                return elem
        except:
            pass
    return None


def save_message_to_inbox(sender, subject, message_text, timestamp):
    """Save a new message to the Inbox directory."""
    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_gmail_{sender.replace(' ', '_')}_message.md"
    filepath = os.path.join(INBOX_DIR, filename)
    
    content = f"""---
created: {timestamp.isoformat()}
source: gmail
status: pending
---

# Email from {sender}

**Subject:** {subject}

**Message:**
"{message_text}"

## Action Required
- Classify: Personal domain
- Route: AI Orchestrator
- Approval: Required (new message)
"""
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Message saved to Inbox: {filename}")
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False


def watch_gmail():
    """Main Gmail watching function."""
    print("Starting Gmail watcher...")
    
    # Validate selectors
    validation = validate_selectors()
    if not validation["valid"]:
        print(f"⚠️ Selector validation issues: {validation['issues']}")
    else:
        print("✅ Selectors loaded successfully")

    storage_state = load_session(STORAGE_FILE)

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(
                headless=False,
                slow_mo=600,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            context = browser.new_context(
                storage_state=storage_state,
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Bypass automation detection
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)

            # Navigate to Gmail
            print("Navigating to Gmail...")
            page.goto("https://accounts.google.com", timeout=get_timeout("page_load"))
            human_delay(5000, 8000)

            # Check if already logged in
            try:
                # Look for inbox or search bar
                selector = get_selector("gmail", "inbox") or "[aria-label='Inbox']"
                page.wait_for_selector(selector, timeout=30000)
                print("Already logged in!")
            except:
                # Login process
                print("Not logged in - performing login...")

                # Click Sign in button if on Gmail landing page
                try:
                    sign_in_btn = page.locator("a:has-text('Sign in'), button:has-text('Sign in')").first
                    if sign_in_btn.is_visible(timeout=5000):
                        sign_in_btn.click()
                        human_delay(2000, 4000)
                        print("Clicked Sign in button")
                except:
                    pass  # Already on login page

                # Enter email
                try:
                    selector = get_selector("gmail", "email_field") or "input[type='email'], input[name='identifier']"
                    email_input = page.locator(selector).first
                    email_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
                    email_input.fill(GMAIL_EMAIL)
                    human_delay(1000, 2000)

                    # Click Next
                    next_btn = page.locator("[id='identifierNext'], button:has-text('Next')").first
                    next_btn.click()
                    human_delay(3000, 5000)
                except Exception as e:
                    print(f"Error entering email: {e}")
                    take_screenshot(page, "gmail_email_input")
                    raise

                # Enter password
                try:
                    selector = get_selector("gmail", "password_field") or "input[type='password'], input[name='password']"
                    password_input = page.locator(selector).first
                    password_input.wait_for(state='visible', timeout=get_timeout("selector_wait"))
                    password_input.fill(GMAIL_PASSWORD)
                    human_delay(1000, 2000)

                    # Click Next
                    next_btn = page.locator("[id='passwordNext'], button:has-text('Next')").first
                    next_btn.click()
                    human_delay(5000, 8000)
                except Exception as e:
                    print(f"Error entering password: {e}")
                    take_screenshot(page, "gmail_password_input")
                    raise

                # Save session after successful login
                save_session(context, STORAGE_FILE)

            # Monitor for new messages
            print("Monitoring for new messages...")
            last_message_count = 0
            
            while True:
                try:
                    # Get current message count (unread messages)
                    try:
                        # Look for unread messages indicator
                        unread_count_elem = page.locator("[aria-label='Unread messages'], [data-tooltip='Unread messages']").first
                        unread_count = int(unread_count_elem.text_content().strip()) if unread_count_elem else 0
                    except:
                        # Fallback: count message rows
                        message_rows = page.locator("[role='article']").all()
                        unread_count = len(message_rows)
                    
                    # If new messages found
                    if unread_count > last_message_count:
                        print(f"New messages detected: {unread_count - last_message_count}")
                        
                        # Process new messages (get latest ones)
                        message_elements = page.locator("[role='article']").all()
                        for i, msg_elem in enumerate(message_elements[:unread_count]):
                            try:
                                # Get sender name
                                sender_elem = msg_elem.locator("[aria-label='Sender'], [data-testid='sender-name']").first
                                sender = sender_elem.text_content(timeout=5000).strip() if sender_elem else "Unknown"
                                
                                # Get subject
                                subject_elem = msg_elem.locator("[aria-label='Subject'], [data-testid='subject']").first
                                subject = subject_elem.text_content(timeout=5000).strip() if subject_elem else "No Subject"
                                
                                # Get message preview
                                preview_elem = msg_elem.locator("[aria-label='Preview'], [data-testid='preview']").first
                                message_text = preview_elem.text_content(timeout=5000).strip() if preview_elem else ""
                                
                                if sender and (subject or message_text):
                                    timestamp = datetime.datetime.now()
                                    save_message_to_inbox(sender, subject, message_text, timestamp)
                                    
                            except Exception as e:
                                print(f"Error processing message {i}: {e}")
                                take_screenshot(page, f"gmail_message_processing_{i}")
                        
                        last_message_count = unread_count
                    
                    # Wait before next check
                    human_delay(60000, 90000)  # Check every 60-90 seconds
                    
                except KeyboardInterrupt:
                    print("\nWatcher stopped by user")
                    break
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    take_screenshot(page, "gmail_monitoring_error")
                    human_delay(30000, 60000)  # Wait longer after error

    except Exception as e:
        print(f"Watcher failed: {e}")
        raise
    finally:
        print("Watcher stopping...")


def main():
    """Main function to run Gmail watcher."""
    print("=" * 60)
    print("Gmail Watcher - Dynamic Selectors")
    print("=" * 60)
    
    # Add Gmail selectors to selector_loader if needed
    try:
        # Ensure Gmail selectors are available
        selectors = {}
        if os.path.exists("selectors.json"):
            with open("selectors.json", 'r') as f:
                selectors = json.load(f)
        
        # Add Gmail selectors if missing
        if "gmail" not in selectors:
            selectors["gmail"] = {
                "inbox": "[aria-label='Inbox'], [data-tooltip='Inbox']",
                "email_field": "input[type='email'], input[name='identifier']",
                "password_field": "input[type='password'], input[name='password']",
                "sender_name": "[aria-label='Sender'], [data-testid='sender-name']",
                "subject": "[aria-label='Subject'], [data-testid='subject']",
                "preview": "[aria-label='Preview'], [data-testid='preview']"
            }
            
            with open("selectors.json", 'w') as f:
                json.dump(selectors, f, indent=2)
            print("Added Gmail selectors to selectors.json")
    except Exception as e:
        print(f"Warning: Could not update selectors.json: {e}")

    try:
        watch_gmail()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        raise
    finally:
        print("Gmail watcher stopped")


if __name__ == "__main__":
    main()