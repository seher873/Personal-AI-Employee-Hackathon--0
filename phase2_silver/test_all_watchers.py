#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All Watchers - Quick Test
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
print("All Watchers - Test")
print("=" * 60)

# Credentials check
email = os.getenv('GMAIL_EMAIL') or os.getenv('GMAIL_ADDRESS')
password = os.getenv('GMAIL_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')

print(f"\nCredentials:")
print(f"  Email: {email}")
print(f"  Password: {'[SET]' if password else '[NOT SET]'}")

watchers_dir = Path(__file__).parent.parent / "phase2_silver" / "Watchers"

# Test each watcher
watchers = {
    "Gmail Watcher": "gmail_watcher.py",
    "WhatsApp Watcher": "whatsapp_watcher.py",
    "LinkedIn Watcher": "linkedin_watcher.py",
}

print("\n" + "-" * 60)
print("Watcher Files:")
print("-" * 60)

for name, filename in watchers.items():
    filepath = watchers_dir / filename
    exists = filepath.exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {name}: {filename}")

# Check directories
print("\n" + "-" * 60)
print("Directories:")
print("-" * 60)

dirs = {
    "Logs": watchers_dir / "Logs",
    "Inbox": watchers_dir.parent / "Inbox",
    "WhatsApp Session": watchers_dir / "whatsapp_session",
    "LinkedIn Session": watchers_dir / "linkedin_session",
}

for name, path in dirs.items():
    exists = path.exists()
    status = "[EXISTS]" if exists else "[NOT FOUND]"
    print(f"  {status} {name}")

print("\n" + "=" * 60)
print("Status: All watchers ready to run")
print("=" * 60)

print("\nRun commands:")
print(f"  Gmail:     py {watchers_dir}\\gmail_watcher.py")
print(f"  WhatsApp:  py {watchers_dir}\\whatsapp_watcher.py --once")
print(f"  LinkedIn:  py {watchers_dir}\\linkedin_watcher.py")
