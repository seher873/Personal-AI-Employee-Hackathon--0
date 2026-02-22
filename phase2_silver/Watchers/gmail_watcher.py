#!/usr/bin/env python3
"""
Gmail watcher for the AI Employee (Silver Tier).
Monitors Gmail inbox for new emails and triggers reasoning workflows.
Requires Python 3.13 or higher.
"""

import sys
import time
import logging
import json
from pathlib import Path
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import schedule
from dotenv import load_dotenv
import requests
import os
import re

# Load environment variables
load_dotenv()

# Check Python version
if sys.version_info < (3, 13):
    print(f"Error: Python 3.13 or higher is required. Current version: {sys.version}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class GmailWatcher:
    """Watches Gmail inbox for new emails and triggers reasoning workflows."""

    def __init__(self):
        self.email_address = os.getenv('GMAIL_ADDRESS')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        self.mcp_server_url = os.getenv('MCP_SERVER_URL', 'http://localhost:3000')

        if not self.email_address or not self.app_password:
            raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set in .env file")

        self.connection = None
        self.last_check = datetime.now() - timedelta(minutes=1)  # Start by checking last 1 minute
        logging.info(f"Initialized Gmail watcher for: {self.email_address}")

    def connect(self):
        """Connect to Gmail IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL('imap.gmail.com')
            self.connection.login(self.email_address, self.app_password)
            self.connection.select('INBOX')
            logging.info("Successfully connected to Gmail")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Gmail: {e}")
            return False

    def decode_mime_words(self, s):
        """Decode MIME encoded words in headers."""
        decoded_fragments = decode_header(s)
        fragments = []
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                if encoding:
                    fragments.append(fragment.decode(encoding))
                else:
                    fragments.append(fragment.decode('utf-8', errors='ignore'))
            else:
                fragments.append(fragment)
        return ''.join(fragments)

    def extract_email_content(self, msg):
        """Extract content from email message."""
        subject = self.decode_mime_words(msg.get("Subject", "No Subject"))
        sender = self.decode_mime_words(msg.get("From", "Unknown Sender"))

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset()
                    body = part.get_payload(decode=True)
                    if body:
                        body = body.decode(charset or 'utf-8', errors='ignore')
                    break
        else:
            charset = msg.get_content_charset()
            body = msg.get_payload(decode=True)
            if body:
                body = body.decode(charset or 'utf-8', errors='ignore')

        return {
            'subject': subject,
            'sender': sender,
            'body': body.strip() if body else "",
            'date': msg.get("Date", "")
        }

    def get_recent_emails(self):
        """Fetch recent emails since last check."""
        if not self.connection:
            if not self.connect():
                return []

        try:
            # Search for emails received since last check
            since_date = self.last_check.strftime('%d-%b-%Y')
            search_criteria = f'(SINCE {since_date})'

            status, messages = self.connection.search(None, search_criteria)

            if status != 'OK':
                logging.error(f"Search failed: {status}")
                return []

            email_ids = messages[0].split()
            recent_emails = []

            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')

                    if status != 'OK':
                        continue

                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract content
                    email_content = self.extract_email_content(msg)

                    # Only include emails received after last check time
                    email_time = email.utils.parsedate_to_datetime(msg.get("Date", ""))
                    if email_time and email_time > self.last_check:
                        recent_emails.append(email_content)

                except Exception as e:
                    logging.error(f"Error processing email {email_id}: {e}")
                    continue

            # Update last check time to now
            self.last_check = datetime.now()

            return recent_emails

        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
            # Try to reconnect
            self.connection = None
            return []

    def _log_reasoning_step(self, message, email_info=None):
        """Log reasoning steps to activity log."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] REASONING: {message}"
        if email_info:
            log_entry += f" (Email: {email_info.get('subject', 'Unknown')})"
        log_entry += "\n"

        # Write to activity log
        log_path = Path(__file__).parent.parent / "Logs" / "activity.log"
        log_path.parent.mkdir(exist_ok=True)  # Ensure Logs directory exists
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

    def _convert_email_to_markdown_task(self, email_data):
        """Convert email to Markdown task file and save to Inbox."""
        try:
            # Create a unique filename based on email and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            subject_clean = re.sub(r'[^\w\s-]', '', email_data['subject'][:50]).strip()
            filename = f"email_{timestamp}_{subject_clean}.md"
            filepath = Path(__file__).parent.parent / "Inbox" / filename

            # Create Markdown content from email
            markdown_content = f"""# {email_data['subject']}

## From
{email_data['sender']}

## Date
{email_data['date']}

## Email Content
{email_data['body']}

## Action Required
Please process this email task.

## Priority
Normal
"""
            # Write the markdown file to the Inbox
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content.strip())

            logging.info(f"Email converted to task file: {filename}")
            self._log_reasoning_step(f"Email converted to task: {filename}")

            return filepath

        except Exception as e:
            self._log_reasoning_step(f"Error converting email to task: {str(e)}", email_data)
            logging.error(f"Error converting email {email_data['subject']} to task: {e}")
            return None

    def check_for_new_emails(self):
        """Check for new emails and convert them to task files."""
        logging.info("Checking for new emails...")

        emails = self.get_recent_emails()

        if emails:
            logging.info(f"Found {len(emails)} new email(s)")

            for email_data in emails:
                logging.info(f"Converting email to task: {email_data['subject']}")
                task_file = self._convert_email_to_markdown_task(email_data)

                if task_file:
                    logging.info(f"Email converted and saved as task: {task_file.name}")
                else:
                    logging.error(f"Failed to convert email to task: {email_data['subject']}")
        else:
            logging.debug("No new emails found")

    def start_monitoring(self):
        """Start monitoring for new emails."""
        logging.info("Starting Gmail monitoring...")

        # Connect to Gmail
        if not self.connect():
            logging.error("Cannot start monitoring without Gmail connection")
            return

        # Schedule email checking every minute
        schedule.every(1).minutes.do(self.check_for_new_emails)

        # Also run an initial check
        self.check_for_new_emails()

        logging.info("Gmail monitoring started. Checking every minute...")
        print("Gmail watcher is running. Press Ctrl+C to stop.")
        print("Silver Tier: Email reasoning workflows will be triggered on email detection.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Gmail watcher stopping...")
        finally:
            if self.connection:
                self.connection.close()
                self.connection.logout()
            logging.info("Gmail watcher stopped.")

def main():
    """Main entry point for the Gmail watcher."""
    try:
        watcher = GmailWatcher()
        watcher.start_monitoring()
    except Exception as e:
        logging.error(f"Gmail watcher failed to start: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()