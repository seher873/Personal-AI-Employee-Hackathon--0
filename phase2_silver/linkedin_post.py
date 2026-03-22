#!/usr/bin/env python3
"""
LinkedIn Quick Post - Simple & Reliable
Opens browser with text in clipboard
"""

import sys
import json
import time
import webbrowser
from pathlib import Path
import pyperclip

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "linkedin_credentials.json"

def main():
    print("=" * 60)
    print("💼 LinkedIn Quick Post")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True, help='Post text')
    args = parser.parse_args()
    
    # Load email for display
    email = "Unknown"
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            email = creds.get('email', 'Unknown')
    
    print(f"📧 Account: {email}")
    print(f"📝 Post: {args.text}")
    print()
    
    # Copy to clipboard
    pyperclip.copy(args.text)
    print("✅ Post text copied to clipboard!")
    
    # Open LinkedIn
    print("🌐 Opening LinkedIn...")
    webbrowser.open("https://www.linkedin.com/feed/")
    
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Wait for LinkedIn to load")
    print("2. Click 'Start a post'")
    print("3. Press Ctrl+V to paste")
    print("4. Click 'Post'")
    print("=" * 60)
    print()
    print("✅ Done! Your post is ready to publish.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
