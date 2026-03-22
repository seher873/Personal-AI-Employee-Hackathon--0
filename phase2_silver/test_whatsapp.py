#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test WhatsApp Watcher - Quick Test
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
print("WhatsApp Watcher - Test")
print("=" * 60)

# Check if Playwright is available
try:
    from playwright.sync_api import sync_playwright
    print("\n[OK] Playwright imported")
except ImportError as e:
    print(f"\n[FAIL] Playwright not installed: {e}")
    print("Run: pip install playwright")
    sys.exit(1)

# Add Watchers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "phase2_silver" / "Watchers"))

try:
    from whatsapp_watcher import WhatsAppWatcher
    print("[OK] WhatsAppWatcher module imported")
    
    # Check directories
    watchers_dir = Path(__file__).parent.parent / "phase2_silver" / "Watchers"
    session_dir = watchers_dir / "whatsapp_session"
    inbox_dir = watchers_dir / "Inbox"
    logs_dir = watchers_dir / "Logs"
    
    print(f"\nDirectories:")
    print(f"  Session: {session_dir.exists()}")
    print(f"  Inbox: {inbox_dir.exists()}")
    print(f"  Logs: {logs_dir.exists()}")
    
    print("\n" + "=" * 60)
    print("WhatsApp Watcher: READY")
    print("=" * 60)
    print("\nTo run WhatsApp Watcher:")
    print(f"  py {watchers_dir}\\whatsapp_watcher.py --once")
    print("\nNote: QR code scan required for first login")
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
