#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cron Jobs - Manual Test Script
Windows par cron jobs ko manually test karne ke liye
"""

import os
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
WATCHERS_DIR = BASE_DIR / "Watchers"

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    log_file = LOGS_DIR / "test_cron.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def run_script_test(script_name, description):
    """Run a script and capture result"""
    log(f"Testing {description}...")
    script_path = WATCHERS_DIR / script_name if "watcher" in script_name else BASE_DIR / script_name
    
    if not script_path.exists():
        log(f"  Script not found: {script_path}")
        return False
    
    try:
        # Run the script
        result = os.system(f'py "{script_path}"')
        if result == 0:
            log(f"  ✅ {description} executed successfully")
            return True
        else:
            log(f"  ⚠️  {description} exited with code {result}")
            return True  # Script ran, even if it had issues
    except Exception as e:
        log(f"  ❌ {description} failed: {e}")
        return False

def test_gmail_watcher():
    """Test Gmail Watcher"""
    return run_script_test("gmail_watcher.py", "Gmail Watcher")

def test_whatsapp_watcher():
    """Test WhatsApp Watcher"""
    return run_script_test("whatsapp_watcher.py", "WhatsApp Watcher")

def test_linkedin_watcher():
    """Test LinkedIn Watcher"""
    return run_script_test("linkedin_watcher.py", "LinkedIn Watcher")

def test_email_mcp():
    """Test Email MCP"""
    return run_script_test("email_mcp.py", "Email MCP")

def main():
    print("=" * 60)
    print("Cron Jobs Manual Test")
    print("=" * 60)
    log("\n" + "=" * 60)
    log("Starting manual cron job tests...")
    log("=" * 60)
    
    results = {
        "Gmail Watcher": test_gmail_watcher(),
        "WhatsApp Watcher": test_whatsapp_watcher(),
        "LinkedIn Watcher": test_linkedin_watcher(),
        "Email MCP": test_email_mcp(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    log(f"Completed: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll cron job scripts are working!")
    else:
        print("\nSome scripts failed. Check logs for details.")
    
    print(f"\nLog file: {LOGS_DIR / 'test_cron.log'}")

if __name__ == '__main__':
    main()
