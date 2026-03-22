#!/usr/bin/env python3
"""
LinkedIn Quick Post - Opens browser with pre-filled post
You just need to click "Post" button
"""

import os
import sys
import json
import time
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

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
    
    # Get credentials
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        email = creds.get('email', '')
        print(f"📧 Email: {email}")
    else:
        email = input("Enter LinkedIn email: ")
    
    print(f"📝 Post: {args.text[:100]}...")
    
    # Create LinkedIn post URL
    # Note: LinkedIn doesn't support pre-filling text via URL anymore
    # But we can open the feed page directly
    
    print("\n🌐 Opening LinkedIn...")
    print("💡 After page loads:")
    print("   1. Click 'Start a post'")
    print("   2. Paste your text")
    print("   3. Click 'Post'")
    
    # Open LinkedIn feed
    webbrowser.open("https://www.linkedin.com/feed/")
    
    print("\n✅ Browser opened!")
    print("   Copy this text for your post:")
    print("-" * 60)
    print(args.text)
    print("-" * 60)
    
    # Also copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(args.text)
        print("\n✅ Text copied to clipboard!")
    except:
        print("\n⚠️  Could not copy to clipboard. Please copy manually.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
