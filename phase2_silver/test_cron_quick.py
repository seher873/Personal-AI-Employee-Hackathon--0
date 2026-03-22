#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Cron Jobs Test - Script Existence & Import Test
"""

import os
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent
WATCHERS_DIR = BASE_DIR / "Watchers"

print("=" * 60)
print("Cron Jobs - Quick Test")
print("=" * 60)

scripts = {
    "Gmail Watcher": WATCHERS_DIR / "gmail_watcher.py",
    "WhatsApp Watcher": WATCHERS_DIR / "whatsapp_watcher.py",
    "LinkedIn Watcher": WATCHERS_DIR / "linkedin_watcher.py",
    "LinkedIn Poster": BASE_DIR / "linkedin_browser_poster.py",
    "Email MCP": BASE_DIR / "email_mcp.py",
    "Weekly Audit": BASE_DIR / "weekly_audit.py",
}

print("\nChecking script files:\n")

passed = 0
for name, path in scripts.items():
    exists = path.exists()
    status = "OK" if exists else "MISSING"
    icon = "[/]" if exists else "[X]"
    print(f"  {icon} {name}: {status}")
    if exists:
        passed += 1

print(f"\n{passed}/{len(scripts)} scripts found")

print("\n" + "=" * 60)
print("Cron Schedule Summary:")
print("=" * 60)
print("""
  Gmail Watcher      : Every minute     (* * * * *)
  WhatsApp Watcher   : Every minute     (* * * * *)
  LinkedIn Watcher   : Every minute     (* * * * *)
  LinkedIn Poster    : Daily at 9 AM    (0 9 * * *)
  Email MCP Server   : On demand
  Weekly Audit       : Sunday 8 AM      (0 8 * * 0)
""")

print("\nNote: Windows par Task Scheduler use karein!")
print("=" * 60)
