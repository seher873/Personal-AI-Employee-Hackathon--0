"""
Gmail OAuth Authentication for Silver Tier - Creates token.json
Run this once to authenticate with Google OAuth
Copy this script to phase2_silver and run it.
"""

import os
import sys
import codecs
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]
CREDENTIALS_FILE = "./Credentials.json"
TOKEN_FILE = "./token.json"

def main():
    print("=" * 60)
    print("Gmail OAuth Authentication - Silver Tier")
    print("=" * 60)
    
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        print("Loading existing token...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token...")
            try:
                creds.refresh(Request())
                print("Token refreshed successfully!")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            print("\nStarting OAuth flow...")
            print("1. A browser will open")
            print("2. Sign in with your Google account")
            print("3. Grant permissions")
            print("4. Token will be saved automatically\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0, open_browser=True)
            print("Authentication successful!")
        
        # Save token
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        print(f"\n✅ Token saved to: {TOKEN_FILE}")
    else:
        print("✅ Existing token is valid!")
    
    # Show token info
    print("\n" + "=" * 60)
    print("Authentication Details")
    print("=" * 60)
    print(f"Token file: {TOKEN_FILE}")
    print(f"Scopes granted:")
    for scope in creds.scopes:
        print(f"  - {scope}")
    print(f"Expiry: {creds.expiry}")
    print("=" * 60)
    
    # Test Gmail API
    print("\nTesting Gmail API connection...")
    try:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print(f"✅ Connected to Gmail API!")
        print(f"Found {len(labels)} labels:")
        for label in labels[:5]:
            print(f"  - {label['name']}")
    except Exception as e:
        print(f"⚠️ API test failed: {e}")
    
    print("\n✅ OAuth Authentication Complete!")
    print("You can now use Gmail API with token.json")

if __name__ == "__main__":
    main()
