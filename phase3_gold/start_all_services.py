#!/usr/bin/env python3
"""
Start All Services - Launches all watchers and posters
"""

import subprocess
import sys
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("=" * 60)
print("Starting All Services")
print("=" * 60)

processes = []

# Start Gmail Watcher
print("\n[1/4] Starting Gmail Watcher...")
try:
    p = subprocess.Popen([sys.executable, "gmail_watcher.py"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(("Gmail Watcher", p))
    print("  ✅ Started")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Start Facebook Poster
print("\n[2/4] Starting Facebook Poster...")
try:
    p = subprocess.Popen([sys.executable, "fb_poster.py"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(("FB Poster", p))
    print("  ✅ Started")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Start Instagram Auto Poster
print("\n[3/4] Starting Instagram Auto Poster...")
try:
    p = subprocess.Popen([sys.executable, "instagram_auto_poster.py"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(("IG Poster", p))
    print("  ✅ Started")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Start Twitter Auto Poster
print("\n[4/4] Starting Twitter Auto Poster...")
try:
    p = subprocess.Popen([sys.executable, "twitter_auto_poster.py"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(("Twitter Poster", p))
    print("  ✅ Started")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print("\n" + "=" * 60)
print("All services started!")
print("Press Ctrl+C to stop all services")
print("=" * 60)

try:
    for name, proc in processes:
        proc.wait()
except KeyboardInterrupt:
    print("\n\nStopping all services...")
    for name, proc in processes:
        proc.terminate()
        print(f"  Stopped {name}")
    print("All services stopped")
