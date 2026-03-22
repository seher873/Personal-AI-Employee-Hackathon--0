#!/usr/bin/env python3
"""
Process Email Tasks
===================
Move processed email tasks from Need_Action to Done folder.

Usage:
- py process_email_tasks.py                    # Move all tasks
- py process_email_tasks.py --check            # Just check, don't move
- py process_email_tasks.py email_*.md         # Move specific file
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
NEED_ACTION_DIR = BASE_DIR / "Need_Action"
DONE_DIR = BASE_DIR / "Done"

def ensure_done_folder():
    """Ensure Done folder exists."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)

def move_to_done(filename: str) -> bool:
    """Move a task file from Need_Action to Done."""
    src = NEED_ACTION_DIR / filename
    dst = DONE_DIR / filename

    if not src.exists():
        print(f"❌ File not found: {src}")
        return False

    # Add completion timestamp to file
    content = src.read_text(encoding='utf-8')
    if "## Status" in content:
        # Update status to Completed
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = content.replace("## Status\nPending", f"## Status\n✅ Completed at {timestamp}")
        content += f"\n\n## Moved to Done\n{timestamp}"
        dst.write_text(content, encoding='utf-8')
        src.unlink()  # Delete original
    else:
        shutil.move(str(src), str(dst))

    print(f"✅ Moved: {filename} → Done/")
    return True

def list_pending_tasks():
    """List all pending tasks in Need_Action folder."""
    if not NEED_ACTION_DIR.exists():
        print("📭 Need_Action folder is empty or doesn't exist")
        return []
    
    tasks = list(NEED_ACTION_DIR.glob("*.md"))
    if not tasks:
        print("📭 No pending tasks")
        return []
    
    print(f"\n📋 Pending Tasks ({len(tasks)}):")
    print("-" * 50)
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task.name}")
    print("-" * 50)
    return tasks

def main():
    ensure_done_folder()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            list_pending_tasks()
            return
        
        # Move specific file(s)
        for filename in sys.argv[1:]:
            move_to_done(filename)
    else:
        # Interactive mode
        tasks = list_pending_tasks()
        
        if not tasks:
            return
        
        print("\nMove all pending tasks to Done? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            for task in tasks:
                move_to_done(task.name)
            print(f"\n✅ Moved {len(tasks)} task(s) to Done/")
        else:
            print("\nSpecify filename(s) to move:")
            print("  py process_email_tasks.py email_20260311_*.md")

if __name__ == "__main__":
    main()
