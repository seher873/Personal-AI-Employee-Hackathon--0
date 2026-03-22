#!/usr/bin/env python3
"""
LinkedIn API Poster - Direct POST request
Bypasses OAuth issues with direct API call
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "linkedin_credentials.json"

def get_credentials():
    """Load LinkedIn credentials"""
    if not CREDENTIALS_FILE.exists():
        print("❌ Credentials file not found!")
        return None, None
    
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)
    
    return creds.get('email'), creds.get('password')

def get_linkedin_token(email, password):
    """Get LinkedIn token using credentials (unofficial method)"""
    print("🔐 Getting LinkedIn session...")
    
    # This uses LinkedIn's internal API
    session = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    session.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
        ('Accept', 'application/vnd.linkedin.normalized+json+2.0'),
    ]
    
    # Step 1: Get CSRF token
    try:
        response = session.open('https://www.linkedin.com/login')
        csrf_token = response.getheader('Set-Cookie')
        if csrf_token:
            print("✅ Got session cookie")
    except Exception as e:
        print(f"⚠️  Session setup: {e}")
    
    return None

def main():
    print("=" * 60)
    print("💼 LinkedIn Direct Poster")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True, help='Post text')
    args = parser.parse_args()
    
    # Get credentials
    email, password = get_credentials()
    if not email or not password:
        print("❌ Could not load credentials")
        return 1
    
    print(f"📧 Email: {email}")
    print(f"📝 Post: {args.text[:50]}...")
    
    # For now, use browser automation
    print("\n🌐 Opening LinkedIn for posting...")
    
    import webbrowser
    webbrowser.open("https://www.linkedin.com/feed/")
    
    print("\n💡 LinkedIn feed opened in browser")
    print("📋 Your post text (copy this):")
    print("=" * 60)
    print(args.text)
    print("=" * 60)
    
    # Copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(args.text)
        print("\n✅ Copied to clipboard!")
    except:
        print("\n⚠️  Please copy the text manually")
    
    print("\nSteps:")
    print("1. Click 'Start a post'")
    print("2. Paste the text (Ctrl+V)")
    print("3. Click 'Post'")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
