"""
Test Facebook Connection
Verifies Facebook Page Access Token and posting capability
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_facebook_connection():
    """Test Facebook API connection"""
    
    access_token = os.getenv('FB_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    
    if not access_token or not page_id:
        print("❌ Missing FB_ACCESS_TOKEN or FB_PAGE_ID in .env")
        return False
    
    print("🔍 Testing Facebook Connection...")
    print(f"   Page ID: {page_id}")
    
    # Test 1: Get Page Info
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        'access_token': access_token,
        'fields': 'id,name,access_token'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Error: {data['error']['message']}")
            return False
        
        print(f"✅ Connected to Page: {data.get('name', 'Unknown')}")
        print(f"   Page ID: {data.get('id', 'Unknown')}")
        
        # Test 2: Check Permissions
        print("\n📋 Checking Permissions...")
        permissions_url = f"https://graph.facebook.com/v18.0/{page_id}/permissions"
        perm_response = requests.get(permissions_url, params={'access_token': access_token})
        perm_data = perm_response.json()
        
        if 'data' in perm_data:
            permissions = [p['permission'] for p in perm_data['data'] if p['status'] == 'granted']
            print(f"   Granted permissions: {len(permissions)}")
            for p in ['pages_manage_posts', 'pages_read_engagement', 'instagram_basic']:
                status = "✅" if p in permissions else "❌"
                print(f"   {status} {p}")
        
        # Test 3: Try to post (optional)
        print("\n🧪 Test Post (optional)...")
        test_message = "Facebook connection test! 🤖 #AIEmployee"
        
        post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        post_params = {
            'access_token': access_token,
            'message': test_message
        }
        
        post_response = requests.post(post_url, params=post_params)
        post_data = post_response.json()
        
        if 'id' in post_data:
            print(f"✅ Test post successful! Post ID: {post_data['id']}")
        else:
            print(f"⚠️  Post failed: {post_data.get('error', {}).get('message', 'Unknown error')}")
        
        print("\n✅ Facebook connection is WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FACEBOOK CONNECTION TEST")
    print("=" * 60)
    test_facebook_connection()
    print("=" * 60)
