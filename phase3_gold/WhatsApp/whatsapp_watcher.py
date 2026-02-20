#!/usr/bin/env python3
"""
WhatsApp Watcher for AI Employee - Silver Tier
Monitors WhatsApp_Inbox folder for incoming messages and converts them to tasks.
"""

import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhatsAppWatcher(FileSystemEventHandler):
    """Handles WhatsApp message files and converts them to tasks."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.whatsapp_inbox = self.project_root / "WhatsApp_Inbox"
        self.inbox = self.project_root / "Inbox"
        self.processed = self.project_root / "WhatsApp_Processed"

        # Ensure directories exist
        self.whatsapp_inbox.mkdir(exist_ok=True)
        self.inbox.mkdir(exist_ok=True)
        self.processed.mkdir(exist_ok=True)

    def on_created(self, event):
        """Handle new WhatsApp message files."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix == '.md':
            logger.info(f"New WhatsApp message detected: {file_path.name}")
            self.process_whatsapp_message(file_path)

    def process_whatsapp_message(self, file_path: Path):
        """Convert WhatsApp message to a task."""
        try:
            # Read the message content
            with open(file_path, 'r', encoding='utf-8') as f:
                message_content = f.read().strip()

            # Extract sender and message info
            lines = message_content.split('\n')
            sender = "Unknown Sender"
            message = message_content

            # Look for sender info (first line often contains sender)
            if lines and lines[0].startswith("From:"):
                sender = lines[0].replace("From:", "").strip()
                message = '\n'.join(lines[1:]).strip()

            # Create task content
            task_content = f"""# WhatsApp Task from {sender}

**Received via WhatsApp**
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Message Content
{message}

## Task Requirements
Please process this WhatsApp message request according to our standard workflow.
"""

            # Create unique task filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_filename = f"whatsapp_{timestamp}_{sender.replace(' ', '_')}.md"
            task_path = self.inbox / task_filename

            # Write task to Inbox
            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(task_content)

            logger.info(f"Created task from WhatsApp: {task_filename}")

            # Move original message to processed folder
            processed_path = self.processed / f"processed_{timestamp}_{file_path.name}"
            file_path.rename(processed_path)
            logger.info(f"Moved WhatsApp message to processed: {processed_path.name}")

            # Log the conversion
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WhatsApp message from {sender} converted to task {task_filename}\n"
            log_path = self.project_root / "Logs" / "whatsapp_activity.log"
            log_path.parent.mkdir(exist_ok=True)
            with open(log_path, 'a') as log_file:
                log_file.write(log_entry)

        except Exception as e:
            logger.error(f"Error processing WhatsApp message {file_path}: {e}")

    def on_modified(self, event):
        """Ignore file modifications."""
        pass

    def on_deleted(self, event):
        """Ignore file deletions."""
        pass

def main():
    """Main function to run the WhatsApp watcher."""
    logger.info("Starting WhatsApp Watcher...")

    # Create watcher instance
    event_handler = WhatsAppWatcher()
    observer = Observer()

    # Schedule the observer
    whatsapp_path = str(Path(__file__).parent.parent / "WhatsApp_Inbox")
    observer.schedule(event_handler, whatsapp_path, recursive=False)

    # Start watching
    observer.start()
    logger.info(f"WhatsApp watcher started. Monitoring: {whatsapp_path}")
    logger.info("Waiting for WhatsApp messages... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping WhatsApp watcher...")
        observer.stop()

    observer.join()
    logger.info("WhatsApp watcher stopped.")

if __name__ == "__main__":
    main()