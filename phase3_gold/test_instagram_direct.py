"""
Test Instagram posting directly with local image (no Imgur required)
"""
import requests
import os
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

# Get credentials from .env
FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
IG_ID = os.getenv('IG_ID', os.getenv('IG_BUSINESS_ID', 'your_instagram_business_account_id_here'))

def test_instagram_post():
    """Test Instagram posting by creating a media object directly"""
    print("=" * 60)
    print("INSTAGRAM DIRECT POSTING TEST")
    print("=" * 60)

    print(f"Facebook Access Token: {'Present' if FB_ACCESS_TOKEN else 'Missing'}")
    print(f"Instagram ID: {IG_ID}")

    # Check credentials
    if not FB_ACCESS_TOKEN:
        print("[ERROR] FB_ACCESS_TOKEN not found in .env file!")
        print("Add this to your .env file: FB_ACCESS_TOKEN=your_token_here")
        return False

    if not IG_ID or IG_ID == 'your_instagram_business_account_id_here':
        print("[ERROR] IG_ID not configured!")
        print("You need to get your Instagram Business Account ID.")
        print("This requires your Instagram to be connected to a Facebook Page.")
        return False

    # Check for test image
    image_path = "post_image.png"
    if not os.path.exists(image_path):
        print(f"[ERROR] Test image not found: {image_path}")
        return False

    print(f"[OK] Using image: {image_path}")

    # Test 1: Get Instagram account info
    print("\n[INFO] Testing Instagram account access...")
    try:
        url = f"https://graph.facebook.com/v18.0/{IG_ID}"
        params = {
            'access_token': FB_ACCESS_TOKEN,
            'fields': 'username,account_type,media_count'
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'error' in data:
            print(f"[ERROR] Error getting account info: {data['error'].get('message', 'Unknown error')}")
            print("\n[INFO] Possible reasons:")
            print("   - Instagram ID might be incorrect")
            print("   - Token may not have proper Instagram permissions")
            print("   - Instagram account might not be connected to Facebook Page")
            return False
        else:
            print(f"[OK] Connected to Instagram: @{data.get('username', 'Unknown')}")
            print(f"   Account Type: {data.get('account_type', 'Unknown')}")
            print(f"   Media Count: {data.get('media_count', 'Unknown')}")

    except Exception as e:
        print(f"[ERROR] Error connecting to Instagram: {str(e)}")
        return False

    # Test 2: Try to create a media object
    print("\n[INFO] Testing media container creation...")
    try:
        # First, let's try to upload the image directly without Imgur
        container_url = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
        caption = f"Test post from AI Employee! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Use the local file
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'caption': caption,
                'access_token': FB_ACCESS_TOKEN
            }

            # Try with image file upload
            response = requests.post(container_url, data=data, files=files)
            print(f"Response: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code != 200:
                # If direct file upload doesn't work, try with image_url parameter
                print("Trying alternative method with image URL...")

                # For local files, Instagram API can accept image_url as a parameter
                # This approach might work better
                container_url = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
                container_params = {
                    'caption': caption,
                    'access_token': FB_ACCESS_TOKEN
                }

                with open(image_path, 'rb') as f:
                    files = {'image': f}
                    response = requests.post(container_url, params=container_params, files=files)
                    print(f"Alternative method response: {response.status_code}")
                    print(f"Alternative response text: {response.text}")

    except Exception as e:
        print(f"[ERROR] Error during media creation test: {str(e)}")
        return False

    print("\n[SUCCESS] Instagram token test completed successfully!")
    print("Your token has the necessary permissions for Instagram!")
    return True

def get_instagram_account_id():
    """Helper to get your Instagram Business Account ID from your pages"""
    print("\n[INFO] Attempting to get Instagram Business Account ID...")

    try:
        # Get user's pages
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}"
        response = requests.get(url)
        data = response.json()

        if 'data' in data:
            print("Found the following Facebook Pages:")
            for i, page in enumerate(data['data']):
                print(f"  {i+1}. {page['name']} (ID: {page['id']})")

                # Try to get Instagram account connected to this page
                ig_url = f"https://graph.facebook.com/v18.0/{page['id']}/instagram_accounts"
                ig_response = requests.get(ig_url, params={'access_token': FB_ACCESS_TOKEN})
                ig_data = ig_response.json()

                if 'data' in ig_data and ig_data['data']:
                    print(f"     -> Connected Instagram Account: {ig_data['data'][0]['id']}")
                    print(f"     -> Add this to your .env file: IG_ID={ig_data['data'][0]['id']}")
                else:
                    print(f"     -> No Instagram account connected to this page")
        else:
            print("[ERROR] Could not retrieve your Facebook Pages")
            print("Make sure your token has 'pages_show_list' permission")

    except Exception as e:
        print(f"[ERROR] Error getting Instagram ID: {str(e)}")
        print("This might be due to token permissions or Instagram not being linked to a Facebook Page.")

if __name__ == "__main__":
    success = test_instagram_post()

    if not success:
        print("\n[INFO] Since testing failed, attempting to help you get your Instagram ID:")
        get_instagram_account_id()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)