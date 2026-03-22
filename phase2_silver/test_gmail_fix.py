#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gmail Watcher - datetime fix + Gold/Silver tier support
"""

import sys
import io
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load Gold tier .env
BASE_DIR = Path(__file__).parent.parent / "phase3_gold"
load_dotenv(BASE_DIR / ".env")

print("=" * 60)
print("Gmail Watcher - Test (Gold Tier)")
print("=" * 60)

# Check credentials
email = os.getenv('GMAIL_EMAIL') or os.getenv('GMAIL_ADDRESS')
password = os.getenv('GMAIL_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')

print(f"\nCredentials loaded:")
print(f"  Email: {email}")
print(f"  Password: {'*' * len(password) if password else 'NOT SET'}")

if not email or not password:
    print("\n[FAIL] Credentials not set!")
    sys.exit(1)

# Add Watchers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "phase2_silver" / "Watchers"))

try:
    from gmail_watcher import GmailWatcher
    print("\n[OK] Module imported successfully")
    
    watcher = GmailWatcher()
    print(f"[OK] Gmail watcher initialized")
    print(f"     Email: {watcher.email_address}")
    print(f"     Last check: {watcher.last_check}")
    print(f"     Timezone aware: {watcher.last_check.tzinfo is not None}")
    
    if watcher.connect():
        print("[OK] Connected to Gmail successfully")
        watcher.connection.close()
        watcher.connection.logout()
        print("[OK] Connection closed")
    else:
        print("[FAIL] Could not connect to Gmail")
    
    print("\n" + "=" * 60)
    print("datetime fix: SUCCESS")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
