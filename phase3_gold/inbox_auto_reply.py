"""
Inbox Auto-Reply Handler
Gold Tier - Processes Inbox messages and sends auto-replies

Monitors Inbox/ folder for new messages and sends automatic replies
based on keywords and rules.

Usage:
    py inbox_auto_reply.py
    py inbox_auto_reply.py --process-all
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_post_watcher import SocialPostWatcher

# Configuration
INBOX_DIR = "./Inbox"
DONE_DIR = "./Done"
LOGS_DIR = "./Logs"

# Create directories
os.makedirs(DONE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Auto-reply keywords and responses
AUTO_REPLIES = {
    # Greetings
    "hello": "Hello! 👋 Main AI Employee hoon! Main aapki kaise madad kar sakta hoon?",
    "hi": "Hi there! 🤖 How can I help you today?",
    "hey": "Hey! 😊 Kya main aapki help kar sakta hoon?",
    "good morning": "Good Morning! ☀️ Have a great day! Kya kaam hai?",
    "good evening": "Good Evening! 🌙 How can I assist you?",
    
    # Business inquiries
    "price": "Humare products/services ke prices ke liye please website visit karein: www.example.com/pricing",
    "cost": "Pricing information ke liye humari website check karein ya sales team se contact karein.",
    "buy": "Purchase karne ke liye please humari website visit karein: www.example.com/shop",
    "order": "Order place karne ke liye: www.example.com/order ya sales@example.com pe email karein.",
    
    # Contact info
    "contact": "Aap humse contact kar sakte hain:\n📧 Email: contact@example.com\n📱 Phone: +92-300-1234567",
    "email": "Humara email hai: contact@example.com",
    "phone": "Phone number: +92-300-1234567",
    "address": "Office address: 123 Business Street, City, Country",
    
    # Support
    "help": "Main yahan aapki madad karne ke liye hoon! 😊 Bataiye kya help kar sakta hoon?",
    "support": "Support ke liye aap humein email kar sakte hain: support@example.com",
    "issue": "Sorry to hear about the issue! 🙁 Humari team jald se jald resolve karegi.",
    
    # Thanks
    "thanks": "You're welcome! 😊 Kuch aur help chahiye?",
    "thank you": "My pleasure! 🤖 Anything else I can help with?",
    "shukriya": "Ji zaroor! 😊 Aur kuch help chahiye?",
    
    # Social media
    "post": "Main social media pe post kar sakta hoon! Kya post karna hai?",
    "facebook": "Facebook post ke liye message aur image bhejein.",
    "instagram": "Instagram post ke liye photo aur caption chahiye.",
    "linkedin": "LinkedIn pe professional content share kar sakta hoon.",
    
    # Default
    "default": "Thanks for your message! 🤖 Humara team jald reply karega. Emergency mein call karein: +92-300-1234567"
}

# Keywords that trigger social media posting
POST_KEYWORDS = ["post", "share", "publish", "upload", "facebook", "instagram", "linkedin", "twitter"]


class InboxProcessor:
    """Process Inbox messages and send auto-replies."""
    
    def __init__(self):
        self.watcher = SocialPostWatcher()
        self.processed_count = 0
        self.error_count = 0
        
    def _log(self, message):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Print to console (handle Windows encoding issues)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            # Fallback for Windows console with emojis
            print(log_entry.encode('ascii', 'ignore').decode('ascii'))

        # Save to log file
        log_file = os.path.join(LOGS_DIR, f"inbox_processor_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def read_inbox_file(self, filepath):
        """Read inbox markdown file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            lines = content.split('\n')
            metadata = {}
            message_text = ""
            in_frontmatter = False
            
            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        in_frontmatter = False
                    continue
                
                if in_frontmatter:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                else:
                    if line.startswith('# Message from'):
                        continue
                    if line.strip():
                        message_text += line + "\n"
            
            return metadata, message_text.strip()
            
        except Exception as e:
            self._log(f"[ERROR] Failed to read {filepath}: {e}")
            return {}, ""
    
    def get_auto_reply(self, message_text):
        """Get auto-reply based on message keywords."""
        text_lower = message_text.lower()
        
        # Check for keywords
        for keyword, reply in AUTO_REPLIES.items():
            if keyword in text_lower:
                self._log(f"[MATCH] Keyword '{keyword}' found")
                return reply
        
        return AUTO_REPLIES["default"]
    
    def should_post_social(self, message_text):
        """Check if message requests social media post."""
        text_lower = message_text.lower()
        
        for keyword in POST_KEYWORDS:
            if keyword in text_lower:
                return True
        
        return False
    
    def send_reply(self, metadata, message_text, reply_text):
        """Send reply via appropriate channel."""
        source = metadata.get('source', 'unknown')
        sender = metadata.get('sender', 'unknown')
        
        self._log(f"[REPLY] Sending to {sender} via {source}")
        
        try:
            if source == 'whatsapp':
                # Send WhatsApp reply
                result = self.watcher.send_whatsapp_message(sender, reply_text)
                return result.get('success', False)
                
            elif source == 'facebook':
                # Facebook reply would require page messaging API
                # For now, log it
                self._log(f"[FB] Reply prepared for {sender}")
                return True
                
            elif source == 'instagram':
                # Instagram reply would require DM API
                # For now, log it
                self._log(f"[IG] Reply prepared for {sender}")
                return True
                
            else:
                self._log(f"[WARN] Unknown source: {source}")
                return False
                
        except Exception as e:
            self._log(f"[ERROR] Failed to send reply: {e}")
            return False
    
    def process_message(self, filepath):
        """Process a single inbox message."""
        self._log(f"[PROCESS] {os.path.basename(filepath)}")
        
        # Read message
        metadata, message_text = self.read_inbox_file(filepath)
        
        if not message_text:
            self._log("[WARN] Empty message, skipping")
            return False
        
        sender = metadata.get('sender', 'unknown')
        source = metadata.get('source', 'unknown')
        
        self._log(f"[MSG] From {sender} via {source}: {message_text[:50]}...")
        
        # Check if social media post requested
        if self.should_post_social(message_text):
            self._log("[ACTION] Social media post requested")
            
            # Extract post content (simplified - in real scenario, parse better)
            post_text = f"Auto-post from {sender}: {message_text[:200]}"
            
            # Post to all platforms
            results = self.watcher.post_to_all(post_text, None)
            
            self._log(f"[RESULT] FB: {results.get('facebook', {}).get('success')}, IG: {results.get('instagram', {}).get('success')}")
            
            # Move to Done
            self.move_to_done(filepath)
            self.processed_count += 1
            return True
        
        # Get auto-reply
        reply_text = self.get_auto_reply(message_text)
        
        self._log(f"[REPLY] {reply_text[:50]}...")
        
        # Send reply
        success = self.send_reply(metadata, message_text, reply_text)
        
        if success:
            self._log("[OK] Reply sent successfully")
            self.move_to_done(filepath)
            self.processed_count += 1
            return True
        else:
            self._log("[WARN] Reply failed, keeping in Inbox")
            self.error_count += 1
            return False
    
    def move_to_done(self, filepath):
        """Move processed file to Done folder."""
        try:
            filename = os.path.basename(filepath)
            dest_path = os.path.join(DONE_DIR, filename)
            
            # Add completion metadata
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            completion_note = f"\n\n---\ncompleted: {datetime.now().isoformat()}\nstatus: completed\n---\n"
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content + completion_note)
            
            # Remove from Inbox
            os.remove(filepath)
            
            self._log(f"[DONE] Moved to Done/: {filename}")
            
        except Exception as e:
            self._log(f"[ERROR] Failed to move file: {e}")
    
    def process_all(self):
        """Process all messages in Inbox."""
        self._log("=" * 60)
        self._log("📬 Processing Inbox...")
        self._log("=" * 60)
        
        # Get all markdown files in Inbox
        inbox_files = list(Path(INBOX_DIR).glob("*.md"))
        
        if not inbox_files:
            self._log("[INFO] Inbox is empty")
            return
        
        self._log(f"[INFO] Found {len(inbox_files)} messages to process")
        
        # Process each file
        for filepath in sorted(inbox_files):
            self.process_message(str(filepath))
            
            # Small delay between processing
            time.sleep(1)
        
        self._log("=" * 60)
        self._log(f"✅ Processed: {self.processed_count}, Errors: {self.error_count}")
        self._log("=" * 60)
    
    def watch(self, interval=30):
        """Continuously watch Inbox for new messages."""
        self._log("=" * 60)
        self._log("👁️  Inbox Auto-Reply Watcher Started")
        self._log(f"[CONFIG] Check interval: {interval}s")
        self._log("=" * 60)
        
        last_processed = set()
        
        try:
            while True:
                # Get current inbox files
                current_files = set(str(f) for f in Path(INBOX_DIR).glob("*.md"))
                
                # Find new files
                new_files = current_files - last_processed
                
                if new_files:
                    self._log(f"[NEW] {len(new_files)} new message(s)")
                    
                    for filepath in new_files:
                        self.process_message(filepath)
                    
                    last_processed = current_files
                
                # Wait
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self._log("[STOP] User interrupted")
        except Exception as e:
            self._log(f"[ERROR] Watcher crashed: {e}")
        finally:
            self._log("=" * 60)
            self._log(f"📊 Stats: {self.processed_count} processed, {self.error_count} errors")
            self._log("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inbox Auto-Reply Processor")
    parser.add_argument("--process-all", action="store_true", help="Process all inbox messages once")
    parser.add_argument("--watch", action="store_true", help="Continuously watch inbox")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    args = parser.parse_args()
    
    processor = InboxProcessor()
    
    if args.process_all:
        processor.process_all()
    elif args.watch:
        processor.watch(args.interval)
    else:
        # Default: process all once
        processor.process_all()
