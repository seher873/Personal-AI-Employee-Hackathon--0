#!/usr/bin/env python3
"""
Simple Instagram API Test
Tests Instagram posting using Graph API
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

def test_instagram_api():
    """Test Instagram API with simple post"""
    
    # Get credentials
    access_token = os.getenv('FB_ACCESS_TOKEN')
    ig_id = os.getenv('IG_ID')
    
    print("=" * 60)
    print("INSTAGRAM API TEST")
    print("=" * 60)
    
    # Check credentials
    if not access_token:
        print("❌ FB_ACCESS_TOKEN not found in .env")
        return False
    
    if not ig_id or ig_id == "your_instagram_business_account_id_here":
        print("❌ IG_ID not configured in .env")
        print("\n💡 You need to add your Instagram Business ID to .env:")
        print("   IG_ID=17841447308298408  (your actual ID)")
        return False
    
    print(f"✅ Access Token: {access_token[:20]}...")
    print(f"✅ Instagram ID: {ig_id}")
    
    # Test 1: Get Account Info
    print("\n" + "=" * 60)
    print("TEST 1: Get Instagram Account Info")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v18.0/{ig_id}"
    params = {
        'access_token': access_token,
        'fields': 'id,username,name,profile_picture_url'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Error: {data['error']['message']}")
            return False
        
        print(f"✅ Connected: @{data.get('username', 'Unknown')}")
        print(f"   Name: {data.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 2: Create a test post
    print("\n" + "=" * 60)
    print("TEST 2: Create Instagram Post")
    print("=" * 60)
    
    caption = "Test post from AI Employee! #AI #Automation #Testing"
    
    # Use a public image URL (Instagram requires public URLs)
    # Using a direct JPG image URL
    image_url = "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1080&h=1080&fit=crop"
    
    print(f"Caption: {caption}")
    print(f"Image URL: {image_url}")
    
    try:
        # Step 1: Create container
        print("\n📸 Creating media container...")
        
        container_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
        container_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': access_token
        }
        
        response = requests.post(container_url, params=container_params)
        
        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            print(f"❌ Container creation failed: {error_msg}")
            return False
        
        container_result = response.json()
        creation_id = container_result.get('id')
        print(f"✅ Container created: {creation_id}")
        
        # Step 2: Wait for processing
        print("⏳ Waiting for Instagram to process...")
        import time
        time.sleep(5)
        
        # Step 3: Publish
        print("📤 Publishing post...")
        
        publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
        publish_params = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        response = requests.post(publish_url, params=publish_params)
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id')
            print(f"✅ POST SUCCESSFUL!")
            print(f"   Post ID: {post_id}")
            print(f"\n🎉 Instagram API is working!")
            return True
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            print(f"❌ Publish failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_instagram_api()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Instagram API is working!")
    else:
        print("❌ TEST FAILED - Check configuration")
    print("=" * 60)
