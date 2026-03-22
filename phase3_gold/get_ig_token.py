"""
Get your Instagram Page Access Token
Run this after getting a fresh token from Facebook Graph API Explorer
"""

import requests

# Step 1: Get token from Graph API Explorer
# Visit: https://developers.facebook.com/tools/explorer/
# Select your app
# Click "Get Token" -> "Get User Access Token"
# Select permissions: instagram_basic, instagram_content_publish, pages_show_list, pages_read_engagement

# Step 2: Exchange for long-lived token (60 days)
def get_long_lived_token(short_token):
    url = "https://graph.facebook.com/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": "YOUR_APP_ID",
        "client_secret": "YOUR_APP_SECRET",
        "fb_exchange_token": short_token
    }
    r = requests.get(url, params=params)
    return r.json()

# Step 3: Get Instagram Business Account ID
def get_ig_account_id(access_token, ig_username):
    url = f"https://graph.facebook.com/v18.0/me/accounts"
    params = {"access_token": access_token}
    r = requests.get(url, params=params)
    data = r.json()
    
    for page in data.get("data", []):
        page_id = page["id"]
        page_token = page["access_token"]
        
        # Get Instagram account linked to this page
        ig_url = f"https://graph.facebook.com/v18.0/{page_id}/instagram_business_account"
        ig_params = {"access_token": page_token}
        ig_r = requests.get(ig_url, params=ig_params)
        ig_data = ig_r.json()
        
        if "id" in ig_data:
            print(f"Instagram ID: {ig_data['id']}")
            print(f"Page Token: {page_token}")
            return ig_data["id"], page_token
    
    return None, None

print("""
============================================
Instagram Token Setup Guide
============================================

1. Visit: https://developers.facebook.com/tools/explorer/

2. Select your App (or create new)

3. Click "Get Token" > "Get User Access Token"

4. Select these permissions:
   - instagram_basic
   - instagram_content_publish  
   - pages_show_list
   - pages_read_engagement

5. Click "Generate Access Token"

6. Copy the token and paste in .env file:
   IG_ACCESS_TOKEN=<paste_here>

7. Get your Instagram Business ID:
   - Go to: https://graph.facebook.com/v18.0/me/accounts?access_token=<YOUR_TOKEN>
   - Find your page ID
   - Then: https://graph.facebook.com/v18.0/<PAGE_ID>/instagram_business_account?access_token=<YOUR_TOKEN>
   - Copy the "id" field
   - Add to .env: IG_ID=<that_id>

============================================
""")
