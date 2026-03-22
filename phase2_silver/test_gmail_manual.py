#!/usr/bin/env python3
"""Manual test for Gmail watcher"""
import sys
sys.path.insert(0, 'Watchers')
from gmail_watcher import GmailWatcher

print("Initializing Gmail watcher...")
w = GmailWatcher()
print(f"Watcher initialized for: {w.email_address}")

print("\nChecking for new emails...")
w.check_for_new_emails()
print("\nDone!")
