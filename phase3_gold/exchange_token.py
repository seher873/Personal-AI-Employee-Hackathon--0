"""
Exchange short-lived token for long-lived token (60 days)
"""
import requests

# Aapka current short-lived token
SHORT_TOKEN = "EAA79P22mTOABQ4pB62f1k5ZAsOkHD4cQIt2lw53GbUk0apbE1FXSDZBVAFYnTMFZATse98ZCGo9rRZBrKxH3ARG4gtZADRits4zixF4bhbnEQWNZCNnCK3848Y5ZBiPqFXl7vkVfQMR5exCtiM7aDZCDQHvIGV2ZCvPc7Rm2a07wFAeZBjjhBdjrnro0L3jLfavGCSIuUlUwdgb75ZAfnPL2LXWLRAClvQiG6ZAhGxZApL"

# App credentials (Graph API Explorer se lo)
APP_ID = "2664214427311628"
APP_SECRET = "13d6aebdeeba86fbfa2cd2d278d4fd1b"

print("=" * 60)
print("Long-Lived Token Generator")
print("=" * 60)

# Step 1: Exchange for long-lived token
url = "https://graph.facebook.com/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_TOKEN
}

print(f"\n[*] Exchanging token...")
print(f"    App ID: {APP_ID}")
print(f"    App Secret: {'*' * len(APP_SECRET) if APP_SECRET != 'YOUR_APP_SECRET' else 'NOT SET'}")

if APP_ID == "YOUR_APP_ID" or APP_SECRET == "YOUR_APP_SECRET":
    print("\n[!] App ID/Secret not set!")
    print("\n📋 App ID/Secret kaise milein:")
    print("   1. https://developers.facebook.com/apps/ pe jao")
    print("   2. Apna app select karo")
    print("   3. Settings → Basic pe jao")
    print("   4. App ID aur App Secret copy karo")
    print("   5. Is script mein paste karo")
else:
    try:
        r = requests.get(url, params=params)
        data = r.json()
        
        if "access_token" in data:
            print(f"\n[OK] Long-lived token generated!")
            print(f"    Token: {data['access_token']}")
            print(f"    Expires: {data.get('expires_in', 'N/A')} seconds")
        else:
            print(f"\n[!] Error: {data}")
    except Exception as e:
        print(f"\n[!] Error: {e}")

print("\n" + "=" * 60)
