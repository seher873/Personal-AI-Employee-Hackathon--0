#!/usr/bin/env python3
"""
WhatsApp Watcher - Gold Tier
============================
Monitor WhatsApp Web for new messages
Follows BaseWatcher pattern
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

from base_watcher import BaseWatcher, INBOX_DIR, NEEDS_ACTION_DIR


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for new messages"""
    
    def __init__(self, check_interval: int = 30):
        super().__init__(check_interval)
        
        # Configuration
        self.session_dir = Path(__file__).parent.parent / "whatsapp_session"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Keywords to prioritize
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important']
        
        self.logger.info("WhatsApp Watcher initialized")
    
    def check_for_updates(self) -> list:
        """Check for new messages (simplified - requires manual browser)"""
        # Note: Full WhatsApp Web automation requires keeping browser open
        # This is a simplified version that checks if WhatsApp Web is accessible
        
        try:
            # For now, just return empty list
            # Full implementation would use Playwright to monitor messages
            self.logger.debug("Checking for WhatsApp messages...")
            return []
            
        except Exception as e:
            self.logger.error(f"Check error: {e}")
            return []
    
    def create_action_file(self, message) -> Path:
        """Create .md file in Needs_Action folder"""
        sender = message.get('sender', 'Unknown')
        text = message.get('text', '')
        timestamp = message.get('timestamp', datetime.now())
        
        # Check priority
        is_priority = any(kw in text.lower() for kw in self.priority_keywords)
        priority = 'high' if is_priority else 'normal'
        
        filename = f"WHATSAPP_{sender.replace(' ', '_')}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = NEEDS_ACTION_DIR / filename
        
        content = f"""---
type: whatsapp_message
sender: {sender}
received: {timestamp.isoformat()}
priority: {priority}
status: pending
---

# WhatsApp Message from {sender}

**Received:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Message

"{text}"

## Suggested Actions

- [ ] Review message
- [ ] Route to AI Orchestrator
- [ ] Respond if needed
- [ ] Archive after processing
"""
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {filename}")
        return filepath


if __name__ == '__main__':
    watcher = WhatsAppWatcher(check_interval=30)
    watcher.run()
