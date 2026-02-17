#!/usr/bin/env python3
"""
Filesystem watcher for the AI Employee Inbox directory.
Monitors for new Markdown task files and logs detection events.
Requires Python 3.13 or higher.
"""

import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore
import hashlib

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

class InboxHandler(FileSystemEventHandler):
    """Handles filesystem events for the Inbox directory."""

    def __init__(self, inbox_path):
        self.inbox_path = Path(inbox_path).resolve()
        self.processed_files = {}  # Track files to prevent duplicate processing
        logging.info(f"Watching directory: {self.inbox_path}")

    def _get_file_hash(self, file_path):
        """Calculate SHA256 hash of file contents to identify unique files."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (OSError, IOError):
            # Return a hash based on file path and modification time if we can't read the file
            stat = file_path.stat()
            return hashlib.sha256(f"{file_path}_{stat.st_mtime}".encode()).hexdigest()

    def _cleanup_old_entries(self, current_time):
        """Remove entries older than 60 seconds to prevent memory buildup."""
        # Create a list of keys to remove to avoid modifying dictionary during iteration
        old_keys = [
            key for key, (_, timestamp) in self.processed_files.items()
            if current_time - timestamp > 60
        ]
        for key in old_keys:
            del self.processed_files[key]

    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process Markdown files
        if file_path.suffix.lower() == '.md':
            # Clean up old entries (older than 60 seconds) to prevent memory buildup
            current_time = time.time()
            self._cleanup_old_entries(current_time)

            # Check if file is being written to (not fully written yet)
            try:
                # Check if file exists and get its size
                if file_path.exists() and file_path.stat().st_size == 0:
                    logging.debug(f"File {file_path.name} is empty, likely still being written")
                    return

                # Calculate file hash to detect if it was already processed recently
                file_hash = self._get_file_hash(file_path)

                # Check if we've seen this file recently (within 5 seconds)
                if file_path.name in self.processed_files:
                    old_hash, old_time = self.processed_files[file_path.name]
                    if file_hash == old_hash and (current_time - old_time) < 5:
                        logging.debug(f"Duplicate event for file: {file_path.name}")
                        return

                # Store the file's hash and timestamp
                self.processed_files[file_path.name] = (file_hash, current_time)

                logging.info(f"New task detected: {file_path.name}")
                print(f"[TASK DETECTED] {file_path.name}")
            except (OSError, IOError) as e:
                logging.warning(f"Error accessing file {file_path.name}: {e}")
        else:
            logging.debug(f"Non-Markdown file ignored: {file_path.name}")

    def on_modified(self, event):
        """Called when a file or directory is modified."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process Markdown files
        if file_path.suffix.lower() == '.md':
            # Clean up old entries (older than 60 seconds) to prevent memory buildup
            current_time = time.time()
            self._cleanup_old_entries(current_time)

            try:
                # Calculate file hash to detect if it was already processed recently
                file_hash = self._get_file_hash(file_path)

                # Check if we've seen this file recently (within 5 seconds)
                if file_path.name in self.processed_files:
                    old_hash, old_time = self.processed_files[file_path.name]
                    if file_hash == old_hash and (current_time - old_time) < 5:
                        logging.debug(f"Duplicate modified event for file: {file_path.name}")
                        return

                # Store the file's hash and timestamp
                self.processed_files[file_path.name] = (file_hash, current_time)

                logging.debug(f"Task modified: {file_path.name}")
            except (OSError, IOError) as e:
                logging.warning(f"Error accessing file {file_path.name}: {e}")

def main():
    """Main entry point for the inbox watcher."""
    # Get the script directory
    script_dir = Path(__file__).parent.parent
    inbox_path = script_dir / "Inbox"

    # Ensure Inbox directory exists
    inbox_path.mkdir(exist_ok=True)

    # Create event handler
    event_handler = InboxHandler(inbox_path)

    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)

    # Start watching
    observer.start()
    logging.info("Inbox watcher started. Monitoring for new tasks...")
    print("Inbox watcher is running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Watcher stopping...")
    finally:
        # Perform final cleanup of observer
        observer.stop()
        observer.join()
        logging.info("Watcher stopped.")

if __name__ == "__main__":
    main()
