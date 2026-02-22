#!/usr/bin/env python3
"""
Filesystem watcher for the AI Employee Inbox directory (Silver Tier).
Monitors for new Markdown task files and triggers reasoning workflows.
Requires Python 3.13 or higher.
"""

import sys
import time
import logging
import json
import re
from pathlib import Path
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore
import hashlib
import requests
import os
from dotenv import load_dotenv

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

class InboxHandler(FileSystemEventHandler):
    """Handles filesystem events for the Inbox directory."""

    def __init__(self, inbox_path):
        self.inbox_path = Path(inbox_path).resolve()
        self.processed_files = {}  # Track files to prevent duplicate processing
        self.mcp_server_url = os.getenv('MCP_SERVER_URL', 'http://localhost:3000')
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

    def _log_reasoning_step(self, message, file_path=None):
        """Log reasoning steps to activity log."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] REASONING: {message}"
        if file_path:
            log_entry += f" (File: {file_path})"
        log_entry += "\n"

        # Write to activity log
        log_path = Path(__file__).parent.parent / "Logs" / "activity.log"
        log_path.parent.mkdir(exist_ok=True)  # Ensure Logs directory exists
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

    def _cleanup_old_entries(self, current_time):
        """Remove entries older than 60 seconds to prevent memory buildup."""
        # Create a list of keys to remove to avoid modifying dictionary during iteration
        old_keys = [
            key for key, (_, timestamp) in self.processed_files.items()
            if current_time - timestamp > 60
        ]
        for key in old_keys:
            del self.processed_files[key]

    def _create_reasoning_plan(self, file_path, task_title, task_content):
        """Create a reasoning plan before acting."""
        try:
            # Create plan content
            plan_content = f"""# Reasoning Plan for: {task_title}

## Original Task
{task_content}

## Task Analysis
- What: [Analysis of what needs to be done]
- Why: [Purpose and importance of the task]
- How: [Proposed approach to complete the task]
- Constraints: [Any limitations or requirements]

## Step-by-Step Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Resources Needed
- [List any required resources]

## Potential Challenges
- [Identify possible issues]
- [Risk mitigation strategies]

## Success Criteria
- [Define what successful completion looks like]

## Decision Log
- {time.strftime('%Y-%m-%d %H:%M:%S')}: Plan created for task
- {time.strftime('%Y-%m-%d %H:%M:%S')}: [Add decision points as needed]
"""

            # Create Plans directory if it doesn't exist
            plans_dir = Path(__file__).parent.parent / "Plans"
            plans_dir.mkdir(exist_ok=True)

            # Create plan filename
            safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', task_title[:50])
            plan_filename = f"Plan_{safe_title}_{int(time.time())}.md"
            plan_path = plans_dir / plan_filename

            # Write the plan file
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content.strip())

            logging.info(f"Reasoning plan created: {plan_filename}")
            self._log_reasoning_step(f"Created reasoning plan: {plan_filename}")

            return plan_path

        except Exception as e:
            self._log_reasoning_step(f"Error creating reasoning plan: {str(e)}", file_path)
            logging.error(f"Error creating reasoning plan for {file_path.name}: {e}")
            return None

    def _trigger_reasoning_workflow(self, file_path):
        """Trigger the reasoning workflow for the detected file."""
        try:
            # Read the task file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract task information
            task_title = "Unknown"
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('#'):
                    task_title = line.strip('# ').strip()
                    break

            # Log the reasoning step
            self._log_reasoning_step(f"Task detected: {file_path.name}, Title: {task_title}")

            # Create reasoning plan before acting (Silver tier requirement)
            plan_path = self._create_reasoning_plan(file_path, task_title, content)

            # Create instruction for MCP server
            instruction = {
                "id": f"{file_path.stem}_{int(time.time())}",
                "action": "process_task",
                "description": f"Process task from file: {file_path.name}",
                "task_file": str(file_path),
                "task_title": task_title,
                "task_content": content,
                "plan_file": str(plan_path) if plan_path else None,
                "timestamp": time.time()
            }

            # Send to MCP server for processing
            try:
                response = requests.post(
                    f"{self.mcp_server_url}/mcp/instruct",
                    json=instruction,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )

                result = response.json()
                self._log_reasoning_step(f"MCP response: {result.get('status', 'unknown')}", file_path)

                logging.info(f"Task {file_path.name} sent to MCP server: {result.get('status', 'unknown')}")

            except requests.exceptions.RequestException as e:
                self._log_reasoning_step(f"MCP connection failed: {str(e)}", file_path)
                logging.error(f"Failed to connect to MCP server: {e}")

        except Exception as e:
            self._log_reasoning_step(f"Error in reasoning workflow: {str(e)}", file_path)
            logging.error(f"Error processing {file_path.name}: {e}")

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

                # Trigger reasoning workflow for Silver Tier
                self._trigger_reasoning_workflow(file_path)

            except (OSError, IOError) as e:
                self._log_reasoning_step(f"Error accessing file: {str(e)}", file_path)
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

    # Ensure required directories exist
    inbox_path.mkdir(exist_ok=True)
    logs_path = script_dir / "Logs"
    logs_path.mkdir(exist_ok=True)
    approvals_path = script_dir / "Approvals"
    approvals_path.mkdir(exist_ok=True)
    skills_path = script_dir / "Skills"
    skills_path.mkdir(exist_ok=True)

    # Create event handler
    event_handler = InboxHandler(inbox_path)

    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)

    # Start watching
    observer.start()
    logging.info("Inbox watcher started. Monitoring for new tasks...")
    print("Inbox watcher is running. Press Ctrl+C to stop.")
    print("Silver Tier: Reasoning workflows will be triggered on task detection.")

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
