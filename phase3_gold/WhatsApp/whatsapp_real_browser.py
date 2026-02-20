#!/usr/bin/env python3
"""
WhatsApp Real-Time Browser Watcher using Playwright

First run: Scan QR code with your phone when browser opens
Next runs: Auto-login if session saved in ./whatsapp_session

Requirements:
- playwright install (run once to install browsers)
- python -m pip install playwright

Usage:
python whatsapp_real_browser.py
"""

import time
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError # type: ignore
import os
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    logger.info("Received interrupt signal. Shutting down gracefully...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

class WhatsAppWatcher:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.last_message = None
        self.retry_count = 0
        self.max_retries = 3

    def start_browser(self):
        """Start browser with persistent context and extended timeouts"""
        logger.info("Starting browser...")
        self.playwright = sync_playwright().start()

        # Create persistent context to save session with extended timeouts
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir='./whatsapp_session',
            headless=False,  # Set to True after first login if desired
            slow_mo=500,  # Slow down actions for visibility
            args=['--disable-blink-features=AutomationControlled'],
            ignore_https_errors=True,  # Ignore HTTPS errors for stability
            bypass_csp=True  # Bypass Content Security Policy
        )

        # Get first page or create new one
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        # Set extended timeouts for page operations
        self.page.set_default_timeout(60000)  # 60 seconds
        self.page.set_default_navigation_timeout(120000)  # 2 minutes

        logger.info("Browser started successfully with extended timeouts")

    def login_to_whatsapp(self):
        """Navigate to WhatsApp Web and handle login"""
        logger.info("Navigating to WhatsApp Web...")
        
        # Use domcontentloaded instead of networkidle (WhatsApp has constant connections)
        try:
            self.page.goto("https://web.whatsapp.com", wait_until='domcontentloaded', timeout=60000)
            logger.info("WhatsApp Web loaded")
        except Exception as e:
            logger.warning(f"Navigation warning: {e}")
            # Page may still be usable even if timeout

        # Wait a bit for page to stabilize
        time.sleep(3)

        # Check if already logged in (chat list visible)
        try:
            self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=30000)
            logger.info("Already logged in!")
            return True
        except PlaywrightTimeoutError:
            logger.info("Not logged in yet. Checking for QR code...")

        # Check for QR code
        try:
            qr_present = self.page.is_visible('div[data-testid="qr-login"]', timeout=10000)
            if qr_present:
                logger.info("QR code visible. Please scan with your phone now...")
        except:
            pass

        # Wait for login (up to 180 seconds - 3 minutes for QR scan)
        try:
            logger.info("Waiting for WhatsApp connection...")
            self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=180000)
            logger.info("WhatsApp connected! Monitoring messages...")
            return True
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for login after 3 minutes. Please try again.")
            return False

    def get_unread_chats(self):
        """Find and return unread chat elements - returns clickable parent items"""
        try:
            # Find all chat list items first
            all_chats = self.page.locator('div[role="listitem"]').all()
            
            if not all_chats:
                logger.debug("No chat items found")
                return []

            unread_chats = []
            
            # Check each chat for unread indicators
            for chat in all_chats[:15]:  # Check first 15 chats
                try:
                    # Get chat HTML to check for unread markers
                    chat_html = chat.inner_html(timeout=3000)
                    
                    # Check for various unread indicators in HTML
                    is_unread = False
                    
                    # Check for unread count badge
                    if 'data-testid="icon-unread-count"' in chat_html:
                        is_unread = True
                        logger.debug("Found unread by badge")
                    
                    # Check for unread aria-label
                    if 'aria-label="unread"' in chat_html.lower():
                        is_unread = True
                        logger.debug("Found unread by aria-label")
                    
                    # Check for green dot indicator class
                    if '.qzmi44lm' in chat_html or 'class="qzmi44lm"' in chat_html:
                        is_unread = True
                        logger.debug("Found unread by green dot")
                    
                    # Check for bold text (unread messages have bold sender names)
                    if 'font-weight: 600' in chat_html or 'font-weight:bold' in chat_html:
                        is_unread = True
                        logger.debug("Found unread by bold text")
                    
                    # Check for specific unread classes
                    unread_classes = ['_ai0c', '_aivd', 'unread']
                    for cls in unread_classes:
                        if cls in chat_html.lower():
                            is_unread = True
                            logger.debug(f"Found unread by class: {cls}")
                            break
                    
                    if is_unread:
                        unread_chats.append(chat)
                        logger.info(f"✓ Found unread chat")
                        
                except Exception as e:
                    logger.debug(f"Chat check failed: {e}")
                    continue

            if unread_chats:
                logger.info(f"Found {len(unread_chats)} unread chats total")
            
            return unread_chats

        except Exception as e:
            logger.error(f"Error finding unread chats: {e}")
            return []

    def get_latest_message(self):
        """Extract latest message from current chat"""
        try:
            # Look for message bubbles
            message_selectors = [
                'div.message-in',  # Received messages
                'div[data-testid="msg-container"]',
                '.message-in .copyable-text'
            ]

            # Get all message elements
            messages = []
            for selector in message_selectors:
                elements = self.page.locator(selector).element_handles()
                if elements:
                    messages.extend(elements)

            if not messages:
                return None

            # Get the last message
            last_msg = messages[-1]

            # Extract text
            try:
                text_element = last_msg.locator('.selectable-text, .copyable-text, span[dir="ltr"]').first
                if text_element:
                    text = text_element.inner_text()
                else:
                    text = last_msg.inner_text()
            except:
                text = last_msg.inner_text()

            # Get sender name (from chat header if available)
            sender = "Unknown"
            try:
                header = self.page.locator('header [data-testid="conversation-info-header"], [title]').first
                if header:
                    sender = header.get_attribute('title') or header.inner_text()
            except:
                pass

            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return {
                'sender': sender,
                'text': text,
                'timestamp': timestamp
            }

        except Exception as e:
            logger.error(f"Error getting latest message: {e}")
            return None

    def save_message(self, message_data):
        """Save message to vault file"""
        try:
            # Create Inbox directory if not exists
            inbox_dir = Path("../Inbox")
            inbox_dir.mkdir(exist_ok=True)

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"new_whatsapp_{timestamp}.md"
            filepath = inbox_dir / filename

            # Format message content
            content = f"""# New WhatsApp Message
From: {message_data['sender']}
Time: {message_data['timestamp']}
Message: {message_data['text']}
"""

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Message saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False

    def monitor_messages(self):
        """Main monitoring loop with extended timeouts"""
        global running
        no_message_count = 0  # Track consecutive checks with no messages

        while running:
            try:
                # Check for unread messages with longer timeout
                unread_chats = self.get_unread_chats()

                if unread_chats:
                    logger.info(f"Found {len(unread_chats)} unread chats")
                    no_message_count = 0  # Reset counter when messages found

                    # Click first unread chat with improved method
                    try:
                        # Scroll into view first
                        unread_chats[0].scroll_into_view_if_needed(timeout=10000)
                        time.sleep(1)
                        
                        # Force click with longer timeout
                        unread_chats[0].click(force=True, timeout=20000)
                        logger.info("✓ Clicked unread chat successfully")
                        time.sleep(3)  # Wait for chat to load
                    except Exception as click_error:
                        logger.error(f"Failed to click chat: {click_error}")
                        # Try JavaScript click
                        try:
                            element_handle = unread_chats[0].element_handle(timeout=5000)
                            self.page.evaluate("(el) => el.click()", element_handle)
                            logger.info("✓ Clicked via JavaScript")
                            time.sleep(3)
                        except Exception as js_error:
                            logger.error(f"JavaScript click also failed: {js_error}")
                            # Try keyboard navigation as fallback
                            logger.info("Trying keyboard navigation...")
                            for i in range(3):
                                self.page.keyboard.press('ArrowDown')
                                time.sleep(0.5)
                            self.page.keyboard.press('Enter')
                            time.sleep(2)

                    # Get latest message with retry
                    message = None
                    for attempt in range(3):
                        message = self.get_latest_message()
                        if message:
                            break
                        time.sleep(2)  # Wait between retries

                    if message and message != self.last_message:
                        logger.info(f"New message from {message['sender']}: {message['text'][:50]}...")

                        # Save to vault
                        self.save_message(message)
                        self.last_message = message

                        # Wait a bit before next check to avoid rapid polling
                        time.sleep(5)
                    else:
                        logger.debug("No new messages in chat")

                else:
                    no_message_count += 1
                    if no_message_count % 10 == 0:  # Log every 10th check
                        logger.info(f"No unread messages for {no_message_count * 10} seconds")
                    else:
                        logger.debug("No unread messages")

                # Wait before next check - increased to 15 seconds for stability
                time.sleep(15)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

                # Check if it's a timeout error
                if "Timeout" in str(e):
                    logger.info("Timeout detected, will retry...")
                    time.sleep(10)  # Extra wait before retry

                # Check if page crashed
                if self.page.is_closed():
                    logger.error("Page closed unexpectedly")
                    if self.retry_count < self.max_retries:
                        self.retry_count += 1
                        logger.info(f"Retrying... ({self.retry_count}/{self.max_retries})")
                        self.reconnect()
                        no_message_count = 0  # Reset counter after reconnection
                    else:
                        logger.error("Max retries reached. Exiting.")
                        running = False
                else:
                    # Page is still open, just had an error - continue monitoring
                    logger.info("Page still open, continuing monitoring...")
                    time.sleep(10)

    def reconnect(self):
        """Reconnect to WhatsApp Web with extended timeout"""
        logger.info("Attempting to reconnect to WhatsApp Web...")
        try:
            if self.page and not self.page.is_closed():
                self.page.close()

            # Create new page with longer timeout settings
            self.page = self.context.new_page()
            self.page.set_default_timeout(60000)  # 60 second default timeout
            self.page.set_default_navigation_timeout(120000)  # 2 minute navigation timeout

            # Login again with retry
            for attempt in range(2):
                if self.login_to_whatsapp():
                    logger.info("Reconnected successfully")
                    self.retry_count = 0  # Reset retry count on successful reconnection
                    return
                else:
                    logger.warning(f"Reconnection attempt {attempt + 1} failed, retrying...")
                    time.sleep(10)

            raise Exception("Failed to reconnect after multiple attempts")

        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            raise

    def run(self):
        """Main run method"""
        try:
            # Start browser
            self.start_browser()

            # Login to WhatsApp
            if not self.login_to_whatsapp():
                return

            # Start monitoring
            self.monitor_messages()

        except Exception as e:
            logger.error(f"Fatal error: {e}")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up...")
        try:
            if self.page and not self.page.is_closed():
                self.page.close()
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    logger.info("Starting WhatsApp Real-Time Watcher...")

    # Check if session directory exists
    if not os.path.exists('./whatsapp_session'):
        logger.info("First run detected. You'll need to scan the QR code.")
    else:
        logger.info("Session directory found. Attempting auto-login...")

    # Create and run watcher
    watcher = WhatsAppWatcher()
    watcher.run()

    logger.info("WhatsApp watcher stopped.")