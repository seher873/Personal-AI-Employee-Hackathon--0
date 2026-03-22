"""
Get Instagram Page Access Token (Never Expires)
Run this script to extract your Page Access Token for Instagram posting

Requirements:
    pip install requests python-dotenv
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def print_step(num, text):
    print(f"\n{'='*60}")
    print(f"STEP {num}: {text}")
    print('='*60)

def get_user_token():
    """Guide user to get initial User Access Token"""
    print_step(1, "Get User Access Token from Facebook Graph API Explorer")
    print("""
1. Visit: https://developers.facebook.com/tools/explorer/

2. Select your App (or create new at developers.facebook.com)

3. Click "Get Token" button -> "Get User Access Token"

4. Select these permissions (check all):
   [X] instagram_basic
   [X] instagram_content_publish
   [X] pages_show_list
   [X] pages_read_engagement
   [X] pages_manage_posts

5. Click "Continue" -> "Done"

6. Copy the "Access Token" shown at top of page
   (Starts with EAAG... or EAAN...)
""")
    
    token = input("Paste your User Access Token here: ").strip()
    return token

def get_pages(user_token):
    """Get all pages accessible to the user"""
    print_step(2, "Fetching your Facebook Pages...")
    
    url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {
        "access_token": user_token,
        "fields": "id,name,access_token,instagram_business_account"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"\n[ERROR] {data['error']['message']}")
            return None
        
        pages = data.get("data", [])
        
        if not pages:
            print("\n[ERROR] No pages found! Create a Facebook Page first.")
            return None
        
        print(f"\n[OK] Found {len(pages)} Page(s):\n")
        
        for i, page in enumerate(pages, 1):
            print(f"{i}. Page: {page['name']}")
            print(f"   Page ID: {page['id']}")
            
            # Check if Instagram is linked
            if "instagram_business_account" in page:
                ig = page["instagram_business_account"]
                print(f"   [IG] Instagram: {ig.get('username', 'Linked')}")
            else:
                print(f"   [WARN] No Instagram linked")
            print()
        
        return pages
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return None

def get_page_token(user_token, page_id):
    """Get Page Access Token for specific page"""
    print_step(3, f"Getting Page Access Token...")
    
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        "access_token": user_token,
        "fields": "access_token,instagram_business_account"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"\n[ERROR] {data['error']['message']}")
            return None, None
        
        page_token = data.get("access_token")
        ig_account = data.get("instagram_business_account")
        
        return page_token, ig_account
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {e}")
        return None, None

def get_instagram_id(page_token, ig_account):
    """Get detailed Instagram Business Account info"""
    if not ig_account or "id" not in ig_account:
        return None
    
    print_step(4, "Fetching Instagram Business Account Details...")
    
    ig_id = ig_account["id"]
    
    url = f"https://graph.facebook.com/v18.0/{ig_id}"
    params = {
        "access_token": page_token,
        "fields": "id,username,name,profile_picture_url"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"\n[ERROR] {data['error']['message']}")
            return None
        
        print(f"\n[OK] Instagram Account Found:")
        print(f"   Name: {data.get('name', 'N/A')}")
        print(f"   Username: @{data.get('username', 'N/A')}")
        print(f"   ID: {data['id']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {e}")
        return None

def save_to_env(page_token, ig_id, ig_username):
    """Save credentials to .env file"""
    print_step(5, "Saving to .env file...")
    
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    
    # Read existing .env
    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()
    
    # Update or add new values
    def update_env_line(content, key, value):
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith(key + "="):
                lines[i] = f"{key}={value}"
                return "\n".join(lines)
        # If not found, add new line
        lines.append(f"{key}={value}")
        return "\n".join(lines)
    
    env_content = update_env_line(env_content, "IG_ACCESS_TOKEN", page_token)
    env_content = update_env_line(env_content, "IG_ID", ig_id)
    env_content = update_env_line(env_content, "IG_USERNAME", ig_username)
    
    # Write back
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"[OK] Saved to: {env_file}")
    print(f"   IG_ACCESS_TOKEN = {page_token[:20]}...")
    print(f"   IG_ID = {ig_id}")
    print(f"   IG_USERNAME = @{ig_username}")

def verify_token(page_token, ig_id):
    """Verify the token works"""
    print_step(6, "Verifying Token...")
    
    url = f"https://graph.facebook.com/v18.0/{ig_id}"
    params = {"access_token": page_token}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"\n[ERROR] Token verification failed: {data['error']['message']}")
            return False
        
        print("\n[OK] Token is VALID!")
        print(f"   Connected to: @{data.get('username', 'Instagram')}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Verification failed: {e}")
        return False

def main():
    # Handle Windows console encoding
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("""
+----------------------------------------------------------+
|     Instagram Page Access Token Generator                |
|     (Never Expires - For Business/Creator Accounts)      |
+----------------------------------------------------------+
    """)
    
    # Step 1: Get User Token
    user_token = get_user_token()
    
    if not user_token:
        print("\n[ERROR] No token provided. Exiting.")
        return
    
    # Step 2: Get Pages
    pages = get_pages(user_token)
    
    if not pages:
        return
    
    # Step 3: Select Page
    if len(pages) == 1:
        selected_page = pages[0]
    else:
        while True:
            try:
                choice = input(f"\nSelect Page (1-{len(pages)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(pages):
                    selected_page = pages[idx]
                    break
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
    
    print(f"\n[OK] Selected: {selected_page['name']}")
    
    # Step 4: Get Page Token
    page_token, ig_account = get_page_token(user_token, selected_page["id"])
    
    if not page_token:
        print("\n[ERROR] Could not get Page Access Token. Exiting.")
        return
    
    print(f"\n[OK] Page Access Token obtained!")
    print(f"   Token starts with: {page_token[:10]}...")
    print(f"   This token NEVER expires!")
    
    # Step 5: Get Instagram Details
    if not ig_account:
        print("\n[WARN] No Instagram Business Account linked to this Page!")
        print("   Please link your Instagram Business/Creator account to this Facebook Page:")
        print("   1. Go to your Facebook Page Settings")
        print("   2. Click 'Instagram'")
        print("   3. Connect your Instagram account")
        print("\n   Then run this script again.")
        return
    
    ig_details = get_instagram_id(page_token, ig_account)
    
    if not ig_details:
        return
    
    # Step 6: Save to .env
    save_to_env(
        page_token,
        ig_details["id"],
        ig_details.get("username", "")
    )
    
    # Step 7: Verify
    if verify_token(page_token, ig_details["id"]):
        print("""
+----------------------------------------------------------+
|  SUCCESS! Your Instagram API is ready to use!            |
|                                                          |
|  You can now use:                                        |
|  - quick_test_post.py                                    |
|  - Any Instagram posting script                          |
+----------------------------------------------------------+
        """)
    else:
        print("\n[WARN] Token saved but verification failed. Check permissions.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
