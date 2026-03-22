#!/usr/bin/env python3
"""
Gmail Watcher - Gold Tier
=========================
Monitor Gmail inbox using IMAP
Follows BaseWatcher pattern
"""

import sys
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime, timedelta

from base_watcher import BaseWatcher, INBOX_DIR, NEEDS_ACTION_DIR


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for new emails"""
    
    def __init__(self, check_interval: int = 120):
        super().__init__(check_interval)
        
        # Gmail configuration
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.email_address = os.getenv("GMAIL_EMAIL", "")
        self.app_password = os.getenv("GMAIL_PASSWORD", "")
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        
        self.connection = None
        self.logger.info(f"Gmail Watcher initialized for: {self.email_address}")
    
    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.app_password)
            self.connection.select('INBOX')
            self.logger.info("Connected to Gmail")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Gmail"""
        try:
            if self.connection:
                self.connection.close()
                self.connection.logout()
        except:
            pass
    
    def check_for_updates(self) -> list:
        """Check for new unread emails"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            # Search for unseen emails
            status, messages = self.connection.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            new_emails = []
            for email_id in email_ids[-10:]:  # Last 10 emails
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    email_id_str = email_id.decode()
                    if email_id_str not in self.processed_items:
                        self.processed_items.add(email_id_str)
                        new_emails.append(msg)
                except Exception as e:
                    self.logger.error(f"Fetch error: {e}")
            
            return new_emails
            
        except Exception as e:
            self.logger.error(f"Check error: {e}")
            return []
    
    def create_action_file(self, msg) -> Path:
        """Create .md file in Needs_Action folder"""
        # Extract subject
        subject = decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', errors='ignore')
        
        # Extract sender
        sender = email.utils.parseaddr(msg['From'])[1]
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        # Get timestamp
        try:
            timestamp = email.utils.parsedate_to_datetime(msg['Date'])
        except:
            timestamp = datetime.now()
        
        # Create action file
        filename = f"GMAIL_{subject.replace(' ', '_')[:30]}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = NEEDS_ACTION_DIR / filename
        
        content = f"""---
type: email
from: {sender}
subject: {subject}
received: {timestamp.isoformat()}
priority: normal
status: pending
---

# Email from {sender}

**Subject:** {subject}

**Received:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Content

{body if body else '[No content]'}

## Suggested Actions

- [ ] Classify email
- [ ] Route to AI Orchestrator
- [ ] Draft response
- [ ] Archive after processing
"""
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {filename}")
        return filepath


if __name__ == '__main__':
    watcher = GmailWatcher(check_interval=120)
    
    try:
        watcher.connect()
        watcher.run()
    except KeyboardInterrupt:
        print("\nGmail Watcher stopped")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        watcher.disconnect()
