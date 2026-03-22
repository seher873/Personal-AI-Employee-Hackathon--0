"""
Test Instagram Connection
Verifies Instagram Business Account and posting capability
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_instagram_connection():
    """Test Instagram Graph API connection"""
    
    access_token = os.getenv('FB_ACCESS_TOKEN')  # Same token for Instagram
    ig_id = os.getenv('IG_ID')
    
    if not access_token or not ig_id:
        print("❌ Missing FB_ACCESS_TOKEN or IG_ID in .env")
        return False
    
    print("🔍 Testing Instagram Connection...")
    print(f"   Instagram Business ID: {ig_id}")
    
    # Test 1: Get Instagram Account Info
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
            print("\n💡 Troubleshooting:")
            print("   1. Make sure Instagram is a Business/Creator account")
            print("   2. Connect Instagram to Facebook Page")
            print("   3. Re-approve Instagram Graph API permissions")
            return False
        
        print(f"✅ Connected to Instagram: @{data.get('username', 'Unknown')}")
        print(f"   Name: {data.get('name', 'Unknown')}")
        print(f"   Profile: {data.get('profile_picture_url', 'N/A')}")
        
        # Test 2: Check Media (recent posts)
        print("\n📋 Checking Recent Media...")
        media_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
        media_params = {
            'access_token': access_token,
            'limit': 3
        }
        
        media_response = requests.get(media_url, params=media_params)
        media_data = media_response.json()
        
        if 'data' in media_data:
            print(f"   Found {len(media_data['data'])} recent posts")
            for i, post in enumerate(media_data['data'][:3], 1):
                print(f"   {i}. {post.get('id', 'Unknown')}")
        
        # Test 3: Check Permissions
        print("\n📋 Checking Instagram Permissions...")
        permissions_url = f"https://graph.facebook.com/v18.0/{ig_id}/permissions"
        perm_response = requests.get(permissions_url, params={'access_token': access_token})
        perm_data = perm_response.json()
        
        if 'data' in perm_data:
            permissions = [p['permission'] for p in perm_data['data'] if p['status'] == 'granted']
            for p in ['instagram_basic', 'instagram_content_publish']:
                status = "✅" if p in permissions else "❌"
                print(f"   {status} {p}")
        
        print("\n✅ Instagram connection is WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("INSTAGRAM CONNECTION TEST")
    print("=" * 60)
    test_instagram_connection()
    print("=" * 60)
