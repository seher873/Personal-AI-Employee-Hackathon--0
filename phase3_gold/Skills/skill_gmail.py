"""
Agent Skill: Gmail Checker
Gold Tier - Email Monitoring

Usage:
    from skill_gmail import GmailSkill
    gmail = GmailSkill()
    gmail.check_inbox()
    emails = gmail.get_emails()
    summary = gmail.generate_summary()
"""

import os
import sys
import json
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
    from config import GMAIL_EMAIL, GMAIL_PASSWORD
except ImportError as e:
    print(f"Import error: {e}")


class GmailSkill:
    """Gmail checking skill with audit logging."""
    
    def __init__(self):
        self.session_dir = "./gmail_session"
        self.storage_file = os.path.join(self.session_dir, "storage_state.json")
        self.user_data_dir = os.path.join(self.session_dir, "chrome_user_data")
        self.log_dir = "./Logs"
        self.inbox_dir = "./Inbox"
        
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.inbox_dir, exist_ok=True)
        
        self.emails = []
        self.processed_hashes = set()
        
        self._log("GmailSkill initialized")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(self.log_dir, f"gmail_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details):
        audit_file = os.path.join(self.log_dir, "gmail_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_email_hash(self, subject, sender):
        content = f"{subject}:{sender}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save_email(self, subject, sender, body, timestamp):
        """Save email to Inbox."""
        email_hash = self._get_email_hash(subject, sender)
        
        if email_hash in self.processed_hashes:
            return False
        
        self.processed_hashes.add(email_hash)
        
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_gmail_{sender.replace('@', '_')}.md"
        filepath = os.path.join(self.inbox_dir, filename)
        
        content = f"""---
created: {timestamp.isoformat()}
source: gmail
sender: {sender}
subject: {subject}
status: pending
---

# Email from {sender}

**Subject:** {subject}

**Received:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Body

{body if body else "[No content]"}

## Actions
- [ ] Classify
- [ ] Route to AI Orchestrator
- [ ] Draft response
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"Email saved: {subject[:50]}...")
            self._save_audit("email_received", {"subject": subject, "sender": sender})
            return True
        except Exception as e:
            self._log(f"Save failed: {e}")
            return False
    
    def _human_delay(self, min_ms=800, max_ms=2000):
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))
    
    def check_inbox(self, max_emails=10):
        """
        Check Gmail inbox for new emails.
        
        Args:
            max_emails: Maximum emails to process
            
        Returns:
            dict: Result with email count
        """
        self._log("Checking Gmail inbox...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=False,
                    slow_mo=500,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to Gmail
                self._log("Opening Gmail...")
                page.goto("https://mail.google.com", timeout=60000, wait_until="domcontentloaded")
                self._human_delay(5000, 8000)
                
                # Check login
                if not self._is_logged_in(page):
                    self._log("❌ Not logged in - Run Gmail login first")
                    browser.close()
                    return {"success": False, "error": "Not logged in"}
                
                self._log("✅ Logged in!")
                
                # Wait for inbox to load
                self._log("Waiting for inbox...")
                self._human_delay(5000, 8000)
                
                # Get emails
                emails = self._get_emails(page, max_emails)
                
                # Process emails
                for email in emails:
                    if self._save_email(email["subject"], email["sender"], email["body"], email["timestamp"]):
                        self.emails.append(email)
                
                browser.close()
                
                self._log(f"Checked inbox: {len(self.emails)} new emails")
                
        except Exception as e:
            self._log(f"Check failed: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "emails_count": len(self.emails),
            "emails": self.emails
        }
    
    def _is_logged_in(self, page):
        """Check if logged in."""
        try:
            selectors = [
                "[aria-label='Inbox']",
                "[data-testid='inbox']",
                "[aria-label='Compose']",
            ]
            for sel in selectors:
                try:
                    if page.is_visible(sel, timeout=5000):
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _get_emails(self, page, max_emails=10):
        """Get emails from inbox."""
        emails = []
        
        try:
            # Email row selectors
            selectors = [
                "[role='row']",
                "tr[role='row']",
                "div[gh='tl'] div",
            ]
            
            for selector in selectors:
                try:
                    rows = page.locator(selector).all()
                    
                    for row in rows[:max_emails]:
                        try:
                            # Get sender
                            sender = ""
                            try:
                                sender_elem = row.locator("[aria-label*=', '], .y6").first
                                sender = sender_elem.text_content(timeout=2000).strip()
                            except:
                                pass
                            
                            # Get subject
                            subject = ""
                            try:
                                subject_elem = row.locator("[aria-label*='Subject'], .y6").first
                                subject = subject_elem.text_content(timeout=2000).strip()
                            except:
                                pass
                            
                            if sender and subject:
                                emails.append({
                                    "sender": sender,
                                    "subject": subject,
                                    "body": "",
                                    "timestamp": datetime.now()
                                })
                        except:
                            continue
                    
                    if emails:
                        break
                        
                except:
                    continue
                    
        except Exception as e:
            self._log(f"Get emails error: {e}")
        
        return emails
    
    def get_emails(self):
        """Get all captured emails."""
        return self.emails
    
    def generate_summary(self):
        """Generate summary."""
        return {
            "platform": "Gmail",
            "total_emails": len(self.emails),
            "recent_emails": self.emails[-10:] if self.emails else []
        }
    
    def get_stats(self):
        return self.generate_summary()


if __name__ == "__main__":
    print("Gmail Skill - Test Mode")
    print("=" * 50)
    
    gmail = GmailSkill()
    result = gmail.check_inbox(max_emails=5)
    
    print("\nResult:", result)
    print("\nSummary:", gmail.generate_summary())
