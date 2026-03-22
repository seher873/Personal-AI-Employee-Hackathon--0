#!/usr/bin/env python3
"""
Facebook/Instagram Token Validator
Checks if your access token is valid and gets account info
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def validate_token():
    """Validate Facebook/Instagram access token"""
    
    access_token = os.getenv('FB_ACCESS_TOKEN')
    ig_id = os.getenv('IG_ID')
    fb_page_id = os.getenv('FB_PAGE_ID')
    
    print("=" * 70)
    print("FACEBOOK/INSTAGRAM TOKEN VALIDATOR")
    print("=" * 70)
    
    if not access_token:
        print("❌ No access token found in .env")
        return
    
    print(f"\n📋 Token Preview: {access_token[:30]}...")
    print(f"   Instagram ID: {ig_id}")
    print(f"   Facebook Page ID: {fb_page_id}")
    
    # Test 1: Validate Token
    print("\n" + "=" * 70)
    print("TEST 1: Validate Access Token")
    print("=" * 70)
    
    try:
        debug_url = "https://graph.facebook.com/debug_token"
        params = {
            'input_token': access_token,
            'access_token': access_token
        }
        
        response = requests.get(debug_url, params=params)
        data = response.json()
        
        if 'data' in data:
            token_info = data['data']
            is_valid = token_info.get('is_valid', False)
            
            if is_valid:
                print(f"✅ Token is VALID")
                print(f"   User ID: {token_info.get('user_id', 'Unknown')}")
                print(f"   App: {token_info.get('app_id', 'Unknown')}")
                
                # Check expiry
                expires_at = token_info.get('expires_at')
                if expires_at:
                    from datetime import datetime
                    expires_dt = datetime.fromtimestamp(expires_at)
                    print(f"   Expires: {expires_dt}")
            else:
                print(f"❌ Token is INVALID or EXPIRED")
                print(f"   Error: {token_info.get('error', 'Unknown error')}")
                print("\n💡 ACTION REQUIRED: Generate a new token")
                print("   1. Go to: https://developers.facebook.com/tools/explorer/")
                print("   2. Select your app")
                print("   3. Click 'Get Token' > 'Get Page Access Token'")
                print("   4. Select your page and grant these permissions:")
                print("      - pages_manage_posts")
                print("      - pages_read_engagement")
                print("      - instagram_basic")
                print("      - instagram_content_publish")
                print("   5. Copy the token and update .env:")
                print("      FB_ACCESS_TOKEN=your_new_token_here")
                return
        else:
            print(f"❌ Unexpected response: {data}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Get Facebook Page Info
    print("\n" + "=" * 70)
    print("TEST 2: Get Facebook Page Info")
    print("=" * 70)
    
    if fb_page_id and fb_page_id != "your_facebook_page_id_here":
        try:
            url = f"https://graph.facebook.com/v18.0/{fb_page_id}"
            params = {
                'access_token': access_token,
                'fields': 'id,name,username'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"❌ Error: {data['error']['message']}")
            else:
                print(f"✅ Facebook Page: {data.get('name', 'Unknown')}")
                print(f"   ID: {data.get('id', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️ FB_PAGE_ID not configured")
    
    # Test 3: Get Instagram Account Info
    print("\n" + "=" * 70)
    print("TEST 3: Get Instagram Business Account Info")
    print("=" * 70)
    
    if ig_id and ig_id != "your_instagram_business_account_id_here":
        try:
            url = f"https://graph.facebook.com/v18.0/{ig_id}"
            params = {
                'access_token': access_token,
                'fields': 'id,username,name,profile_picture_url'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"❌ Error: {data['error']['message']}")
                print("\n💡 Possible Issues:")
                print("   1. Instagram account not connected to Facebook Page")
                print("   2. Instagram account is not a Business/Creator account")
                print("   3. Token doesn't have Instagram permissions")
            else:
                print(f"✅ Instagram Account: @{data.get('username', 'Unknown')}")
                print(f"   Name: {data.get('name', 'Unknown')}")
                print(f"   ID: {data.get('id', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️ IG_ID not configured")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if fb_page_id and fb_page_id != "your_facebook_page_id_here":
        print("✅ FB_PAGE_ID is configured")
    else:
        print("❌ FB_PAGE_ID needs to be set")
    
    if ig_id and ig_id != "your_instagram_business_account_id_here":
        print("✅ IG_ID is configured")
    else:
        print("❌ IG_ID needs to be set")
    
    print("\n💡 Next Steps:")
    print("   1. Make sure all credentials are valid")
    print("   2. Run: py test_instagram_api_simple.py")
    print("   3. Post to Instagram!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    validate_token()
