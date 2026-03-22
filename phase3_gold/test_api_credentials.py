"""
Test API Credentials
Gold Tier - Verify Facebook, Instagram, WhatsApp API setup

Run this script to test if your API credentials are working correctly.
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    FB_ACCESS_TOKEN, FB_PAGE_ID,
    IG_ID,
    WHATSAPP_PHONE, WHATSAPP_API_KEY
)


def test_facebook_api():
    """Test Facebook API credentials."""
    print("\n" + "=" * 60)
    print("Testing Facebook API")
    print("=" * 60)
    
    if not FB_ACCESS_TOKEN:
        print("❌ FB_ACCESS_TOKEN not configured")
        return False
    
    if not FB_PAGE_ID:
        print("❌ FB_PAGE_ID not configured")
        return False
    
    print(f"✅ Access Token: {FB_ACCESS_TOKEN[:20]}...{FB_ACCESS_TOKEN[-10:]}")
    print(f"✅ Page ID: {FB_PAGE_ID}")
    
    # Test API call
    try:
        import requests
        
        url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}"
        params = {
            'access_token': FB_ACCESS_TOKEN,
            'fields': 'name,about'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection Successful!")
            print(f"   Page Name: {data.get('name', 'N/A')}")
            print(f"   About: {data.get('about', 'N/A')}")
            return True
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            print(f"❌ API Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_instagram_api():
    """Test Instagram API credentials."""
    print("\n" + "=" * 60)
    print("Testing Instagram API")
    print("=" * 60)
    
    if not IG_ID:
        print("❌ IG_ID not configured")
        return False
    
    if not FB_ACCESS_TOKEN:
        print("❌ FB_ACCESS_TOKEN not configured (required for Instagram)")
        return False
    
    print(f"✅ Instagram ID: {IG_ID}")
    print(f"✅ Access Token: {FB_ACCESS_TOKEN[:20]}...{FB_ACCESS_TOKEN[-10:]}")
    
    # Test API call
    try:
        import requests
        
        url = f"https://graph.facebook.com/v18.0/{IG_ID}"
        params = {
            'access_token': FB_ACCESS_TOKEN,
            'fields': 'username,biography'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection Successful!")
            print(f"   Username: {data.get('username', 'N/A')}")
            print(f"   Bio: {data.get('biography', 'N/A')[:50]}...")
            return True
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            print(f"❌ API Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_whatsapp_api():
    """Test WhatsApp API credentials."""
    print("\n" + "=" * 60)
    print("Testing WhatsApp API")
    print("=" * 60)
    
    if not WHATSAPP_PHONE:
        print("⚠️ WHATSAPP_PHONE not configured (optional)")
        return None
    
    if not WHATSAPP_API_KEY:
        print("⚠️ WHATSAPP_API_KEY not configured (optional)")
        return None
    
    print(f"✅ Phone Number ID: {WHATSAPP_PHONE}")
    print(f"✅ API Key: {WHATSAPP_API_KEY[:10]}...{WHATSAPP_API_KEY[-10:]}")
    
    # Test API call
    try:
        import requests
        
        url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE}"
        params = {
            'fields': 'name,phone_number'
        }
        headers = {
            'Authorization': f'Bearer {WHATSAPP_API_KEY}'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection Successful!")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Phone: {data.get('phone_number', 'N/A')}")
            return True
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            print(f"❌ API Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("API Credentials Test Suite")
    print("=" * 60)
    
    results = {
        "Facebook": test_facebook_api(),
        "Instagram": test_instagram_api(),
        "WhatsApp": test_whatsapp_api()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for platform, result in results.items():
        if result is True:
            print(f"✅ {platform}: PASSED")
        elif result is False:
            print(f"❌ {platform}: FAILED")
        else:
            print(f"⚠️ {platform}: NOT CONFIGURED (optional)")
    
    print("=" * 60)
    
    # Overall status
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    
    if failed > 0:
        print(f"\n⚠️ {failed} platform(s) failed. Check credentials in .env file.")
    elif passed > 0:
        print(f"\n✅ {passed} platform(s) ready for posting!")
    else:
        print(f"\n⚠️ No platforms configured. Set up credentials in .env file.")
    
    print("\nNext steps:")
    print("1. Fix any failed tests by updating .env credentials")
    print("2. Run: py social_post_watcher.py --post \"Hello World\"")
    print("3. Or run: py social_post_watcher.py --watch")


if __name__ == "__main__":
    main()
