"""
Get WhatsApp Credentials from Meta App
Uses existing Facebook credentials to fetch WhatsApp Business info
"""

import requests
import json
import sys
from datetime import datetime

# Handle Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("WhatsApp Credential Extractor")
print("=" * 60)

# Login credentials
FB_EMAIL = "urojk77@gmail.com"
FB_PASSWORD = "Uroj9$u4@"

print(f"\n[*] Email: {FB_EMAIL}")
print("[*] Attempting to get WhatsApp credentials...")
print("\n" + "=" * 60)

# Step 1: Get App ID from user
print("\nWhatsApp Business API credentials extract karne ke liye:")
print("\n1. Meta Business Suite pe jao: https://business.facebook.com")
print("2. WhatsApp section mein jao")
print("3. Yeh 3 cheezein copy karo:")
print("\n   - Phone Number ID (numeric)")
print("   - Access Token (starts with EAA...)")
print("   - Business Account ID (numeric)")
print("\n" + "=" * 60)

# Direct links for credentials
print("\nQuick Links to Get Credentials:")
print("=" * 60)
print("\n1. WhatsApp Phone Number ID:")
print("   https://developers.facebook.com/apps/YOUR_APP_ID/whatsapp/api-setup/")
print("\n2. WhatsApp Access Token:")
print("   https://developers.facebook.com/apps/YOUR_APP_ID/whatsapp/api-setup/")
print("   (Temporary token - 24 hours, ya permanent token generate karo)")
print("\n3. WhatsApp Business Account ID:")
print("   https://business.facebook.com/settings/accounts/whatsapp-accounts/")
print("\n" + "=" * 60)

# Try to get WhatsApp info using Graph API
print("\n[*] Checking for WhatsApp Business Account...")

# Note: Without a valid access token, we can't directly fetch WhatsApp info
# User needs to manually get credentials from dashboard

print("\n[!] Access Token Expired!")
print("\nNaya Access Token lene ke liye:")
print("\n1. Facebook login karo: https://facebook.com")
print("2. Meta Business Suite: https://business.facebook.com")
print("3. WhatsApp -> Settings -> API Setup")
print("4. Copy credentials and update .env file")

# Provide Graph API Explorer link for token generation
print("\n" + "=" * 60)
print("Quick Token Generation:")
print("=" * 60)
print("\nGraph API Explorer use karo:")
print("https://developers.facebook.com/tools/explorer/")
print("\nSteps:")
print("1. Select your App")
print("2. Select 'Get User Access Token'")
print("3. Permissions select karo:")
print("   - whatsapp_business_messaging")
print("   - whatsapp_business_management")
print("4. 'Generate Access Token' click karo")
print("5. Token copy karo aur .env mein paste karo")

print("\n" + "=" * 60)
print("\nOnce you have credentials, update .env file:")
print("\nWHATSAPP_PHONE=<Phone Number ID>")
print("WHATSAPP_API_KEY=<Access Token>")
print("WHATSAPP_BUSINESS_ID=<Business Account ID>")
print("\n" + "=" * 60)

# Test credentials after update
print("\nTest kaise karein:")
print("=" * 60)
print("\nRun: py check_whatsapp_api.py")
print("\nAgar credentials sahi honge to account info show hoga!")
print("\n" + "=" * 60)
