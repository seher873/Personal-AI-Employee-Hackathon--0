"""
Agent Skill: WhatsApp Watcher
Gold Tier - Message Monitoring

Usage:
    from skill_whatsapp import WhatsAppSkill
    wa = WhatsAppSkill()
    wa.start_monitoring(duration=3600)  # Monitor for 1 hour
    messages = wa.get_messages()
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
except ImportError as e:
    print(f"Import error: {e}")


class WhatsAppSkill:
    """WhatsApp message monitoring skill with audit logging."""
    
    def __init__(self):
        self.session_dir = "./whatsapp_session"
        self.storage_file = os.path.join(self.session_dir, "storage_state.json")
        self.user_data_dir = os.path.join(self.session_dir, "chrome_user_data")
        self.log_dir = "./Logs"
        self.inbox_dir = "./Inbox"
        
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.inbox_dir, exist_ok=True)
        
        self.messages = []
        self.processed_hashes = set()
        self.is_monitoring = False
        
        self._log("WhatsAppSkill initialized")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(self.log_dir, f"whatsapp_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details):
        audit_file = os.path.join(self.log_dir, "whatsapp_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_message_hash(self, sender, text):
        content = f"{sender}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save_message(self, sender, text, timestamp):
        """Save message to Inbox."""
        msg_hash = self._get_message_hash(sender, text)
        
        if msg_hash in self.processed_hashes:
            return False
        
        self.processed_hashes.add(msg_hash)
        
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_whatsapp_{sender.replace(' ', '_')}.md"
        filepath = os.path.join(self.inbox_dir, filename)
        
        content = f"""---
created: {timestamp.isoformat()}
source: whatsapp
sender: {sender}
status: pending
---

# WhatsApp Message from {sender}

**Received:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Message

"{text}"

## Actions
- [ ] Review
- [ ] Route to AI Orchestrator
- [ ] Respond if needed
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"Message saved: {filename}")
            self._save_audit("message_received", {"sender": sender, "text": text[:100]})
            return True
        except Exception as e:
            self._log(f"Save failed: {e}")
            return False
    
    def _human_delay(self, min_ms=800, max_ms=2000):
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))
    
    def start_monitoring(self, duration=3600, check_interval=5):
        """
        Start monitoring WhatsApp for new messages.
        
        Args:
            duration: How long to monitor (seconds)
            check_interval: How often to check (seconds)
            
        Returns:
            dict: Summary of monitoring session
        """
        self._log(f"Starting monitoring for {duration} seconds...")
        self.is_monitoring = True
        start_time = time.time()
        
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
                
                # Navigate to WhatsApp Web
                self._log("Opening WhatsApp Web...")
                page.goto("https://web.whatsapp.com", timeout=60000, wait_until="domcontentloaded")
                self._human_delay(5000, 8000)
                
                # Check login
                if not self._is_logged_in(page):
                    self._log("⚠️ Not logged in - Please scan QR code")
                    self._wait_for_login(page, timeout=120)
                
                self._log("✅ Logged in!")
                
                # Instructions
                self._log("=" * 50)
                self._log("INSTRUCTIONS:")
                self._log("1. Click on a chat to monitor it")
                self._log("2. New messages will be saved to ./Inbox/")
                self._log("3. Press Ctrl+C to stop")
                self._log("=" * 50)
                
                # Wait for user to select chat
                self._log("Selecting chat... (10s)")
                self._human_delay(10000, 12000)
                
                # Monitor loop
                last_count = 0
                check_count = 0
                
                while self.is_monitoring and (time.time() - start_time) < duration:
                    try:
                        elapsed = int(time.time() - start_time)
                        
                        # Check connection
                        if not self._is_logged_in(page):
                            self._log("⚠️ Connection lost!")
                            self._human_delay(5000, 10000)
                            continue
                        
                        # Get messages
                        messages = self._get_messages(page)
                        
                        # Process new messages
                        for msg in messages:
                            if self._save_message(msg["sender"], msg["text"], msg["timestamp"]):
                                self.messages.append(msg)
                                self._log(f"📨 {msg['sender']}: {msg['text'][:50]}...")
                        
                        # Status update
                        check_count += 1
                        if check_count % 6 == 0:
                            self._log(f"Monitoring... ({elapsed}s, {len(self.messages)} messages)")
                        
                        self._human_delay(check_interval * 1000, (check_interval + 2) * 1000)
                        
                    except KeyboardInterrupt:
                        self._log("Stopped by user")
                        break
                    except Exception as e:
                        self._log(f"Error: {e}")
                        self._human_delay(10000, 15000)
                
                # Summary
                elapsed = int(time.time() - start_time)
                self._log(f"\nMonitoring complete: {elapsed}s, {len(self.messages)} messages")
                
                browser.close()
                
        except Exception as e:
            self._log(f"Monitoring failed: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "duration": elapsed,
            "messages_count": len(self.messages),
            "messages": self.messages
        }
    
    def _wait_for_login(self, page, timeout=120):
        """Wait for QR scan and login."""
        self._log("Waiting for QR code scan...")
        start = time.time()
        
        while (time.time() - start) < timeout:
            if self._is_logged_in(page):
                self._log("✅ Logged in!")
                return True
            
            elapsed = int(time.time() - start)
            if elapsed % 15 == 14:
                self._log(f"  Waiting... ({elapsed}s)")
            
            time.sleep(2)
        
        self._log("❌ Login timeout!")
        return False
    
    def _is_logged_in(self, page):
        """Check if logged in."""
        try:
            selectors = [
                "[data-testid='chatlist']",
                "[data-testid='search']",
                "[title*='Search']",
            ]
            for sel in selectors:
                try:
                    if page.is_visible(sel, timeout=3000):
                        return True
                except:
                    continue
            
            # Check for QR code (NOT logged in)
            try:
                if page.is_visible("[data-testid='qr']", timeout=3000):
                    return False
            except:
                pass
            
            return True
        except:
            return False
    
    def _get_messages(self, page):
        """Get messages from current chat."""
        messages = []
        
        try:
            # Message selectors
            selectors = [
                "[data-testid='msg-container']",
                "span.selectable-text",
                "div[role='row']",
            ]
            
            for selector in selectors:
                try:
                    elems = page.locator(selector).all()
                    if elems:
                        for elem in elems[-5:]:  # Last 5 messages
                            try:
                                text = ""
                                sender = "Contact"
                                
                                # Get text
                                try:
                                    text_elem = elem.locator("span.selectable-text, [data-testid='msg-text']").first
                                    text = text_elem.text_content(timeout=2000).strip()
                                except:
                                    pass
                                
                                # Get sender
                                try:
                                    sender_elem = elem.locator("[data-testid='sender-name']").first
                                    sender = sender_elem.text_content(timeout=2000).strip()
                                except:
                                    pass
                                
                                if text:
                                    messages.append({
                                        "sender": sender,
                                        "text": text,
                                        "timestamp": datetime.now()
                                    })
                            except:
                                continue
                        
                        if messages:
                            break
                except:
                    continue
                    
        except Exception as e:
            self._log(f"Get messages error: {e}")
        
        return messages
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self._log("Stopping monitoring...")
        self.is_monitoring = False
    
    def get_messages(self):
        """Get all captured messages."""
        return self.messages
    
    def generate_summary(self):
        """Generate monitoring summary."""
        return {
            "platform": "WhatsApp",
            "total_messages": len(self.messages),
            "is_monitoring": self.is_monitoring,
            "recent_messages": self.messages[-10:] if self.messages else []
        }


if __name__ == "__main__":
    print("WhatsApp Skill - Test Mode")
    print("=" * 50)
    
    wa = WhatsAppSkill()
    result = wa.start_monitoring(duration=60)  # Test for 60 seconds
    
    print("\nResult:", result)
    print("\nSummary:", wa.generate_summary())
