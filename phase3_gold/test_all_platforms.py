"""
Test All Platforms Together
Facebook + Instagram + WhatsApp
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_all_platforms():
    """Test all three platforms together"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING ALL PLATFORMS - META BUSINESS APP")
    print("=" * 70)
    
    results = {
        'Facebook': False,
        'Instagram': False,
        'WhatsApp': False
    }
    
    # ========== FACEBOOK ==========
    print("\n" + "=" * 70)
    print("1️⃣  FACEBOOK TEST")
    print("=" * 70)
    
    fb_token = os.getenv('FB_ACCESS_TOKEN')
    fb_page_id = os.getenv('FB_PAGE_ID')
    
    if fb_token and fb_page_id:
        try:
            url = f"https://graph.facebook.com/v18.0/{fb_page_id}"
            params = {'access_token': fb_token, 'fields': 'id,name'}
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'id' in data:
                print(f"✅ Facebook: Connected to '{data['name']}'")
                results['Facebook'] = True
            else:
                print(f"❌ Facebook: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Facebook: {str(e)}")
    else:
        print("❌ Facebook: Missing credentials in .env")
    
    # ========== INSTAGRAM ==========
    print("\n" + "=" * 70)
    print("2️⃣  INSTAGRAM TEST")
    print("=" * 70)
    
    ig_token = os.getenv('FB_ACCESS_TOKEN')  # Same token
    ig_id = os.getenv('IG_ID')
    
    if ig_token and ig_id:
        try:
            url = f"https://graph.facebook.com/v18.0/{ig_id}"
            params = {'access_token': ig_token, 'fields': 'id,username'}
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'id' in data:
                print(f"✅ Instagram: Connected to @{data.get('username', 'Unknown')}")
                results['Instagram'] = True
            else:
                print(f"❌ Instagram: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Instagram: {str(e)}")
    else:
        print("❌ Instagram: Missing credentials in .env")
    
    # ========== WHATSAPP ==========
    print("\n" + "=" * 70)
    print("3️⃣  WHATSAPP TEST")
    print("=" * 70)
    
    wa_phone = os.getenv('WHATSAPP_PHONE')
    wa_token = os.getenv('WHATSAPP_API_KEY')
    
    if wa_phone and wa_token:
        try:
            url = f"https://graph.facebook.com/v18.0/{wa_phone}"
            params = {'access_token': wa_token, 'fields': 'id,verified_name'}
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'id' in data:
                print(f"✅ WhatsApp: Connected to '{data.get('verified_name', 'Unknown')}'")
                results['WhatsApp'] = True
            else:
                print(f"❌ WhatsApp: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ WhatsApp: {str(e)}")
    else:
        print("❌ WhatsApp: Missing credentials in .env")
    
    # ========== SUMMARY ==========
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    total = len(results)
    success = sum(1 for v in results.values() if v)
    
    for platform, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {platform}: {'CONNECTED' if status else 'NOT CONNECTED'}")
    
    print(f"\nTotal: {success}/{total} platforms connected")
    
    if success == total:
        print("\n🎉 SUCCESS! All platforms are connected!")
        print("\n💡 Next steps:")
        print("   1. Update .env with your new credentials")
        print("   2. Run: py test_all_platforms.py")
        print("   3. Start using the AI Employee system!")
    else:
        print("\n⚠️  Some platforms are not connected yet.")
        print("   Follow NEW_APP_SETUP_GUIDE.md to complete setup")
    
    print("=" * 70 + "\n")
    
    return success == total

if __name__ == "__main__":
    test_all_platforms()
