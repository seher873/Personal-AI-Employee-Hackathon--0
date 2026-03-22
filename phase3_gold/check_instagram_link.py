"""
Check Instagram Connection Status
"""
import requests
import json

# Current credentials
USER_TOKEN = "EAANVcE3rCUYBQ0o5QhMm9dDvPZAxCeaMcdYxyz0ZAJBZCZAVfXFwPidPoZCARHoaZCRPY1oAg9J84QGuIzUdqwZBkmYdNcv5JSiq2bKpspMBiowZB51dZAarH1qWQtzYo0GWq8HQb5tmzicMZChclz9bqHlkTLmW9L13egtKhcU2tYs1uDVlftl3U2FIlg8zSiscTD0BSz7tJRU4Gh9erJfRZA1LINzsbFz9jhAntyzuQW7eYVIJSyh3usVSXRPZCx13ZAIPkDwvEa23LBKHHFOhbjqnHkBv6MoaK"
PAGE_ID = "946427518563399"

print("=" * 60)
print("Instagram Connection Check")
print("=" * 60)

# Step 1: Check Page Access
print("\n[1] Checking Page Access...")
page_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}"
page_params = {
    "access_token": USER_TOKEN,
    "fields": "id,name,access_token"
}
page_r = requests.get(page_url, params=page_params)
page_data = page_r.json()

if "error" in page_data:
    print(f"    [ERROR] {page_data['error']['message']}")
else:
    print(f"    [OK] Page: {page_data['name']}")
    print(f"    [OK] Page ID: {page_data['id']}")
    PAGE_TOKEN = page_data.get("access_token", "")
    
    # Step 2: Check Instagram Business Account
    print("\n[2] Checking Instagram Business Account...")
    ig_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/instagram_business_account"
    ig_params = {"access_token": PAGE_TOKEN}
    ig_r = requests.get(ig_url, params=ig_params)
    ig_data = ig_r.json()
    
    if "error" in ig_data:
        print(f"    [ERROR] {ig_data['error']['message']}")
        print("\n" + "=" * 60)
        print("Instagram NOT linked yet!")
        print("=" * 60)
        print("""
Next Steps:
1. Make sure Instagram is Business/Creator account (not Personal)
   - Instagram App → Settings → Account type
   - Switch to "Professional Account" if needed

2. Link Instagram to Facebook Page:
   - https://facebook.com/{PAGE_ID}/settings/instagram
   - Click "Connect Account"
   - Login with Instagram

3. After linking, run this script again
        """)
    else:
        print(f"    [OK] Instagram Connected!")
        print(f"    [OK] IG Username: @{ig_data.get('username', 'N/A')}")
        print(f"    [OK] IG ID: {ig_data['id']}")
        
        # Step 3: Update .env
        print("\n[3] Updating .env file...")
        import os
        from dotenv import load_dotenv
        
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Update IG_ID
        import re
        content = re.sub(r'IG_ID=.*', f'IG_ID={ig_data["id"]}', content)
        content = re.sub(r'IG_ACCESS_TOKEN=.*', f'IG_ACCESS_TOKEN={PAGE_TOKEN}', content)
        
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"    [OK] .env updated!")
        print(f"    [OK] New IG_ID: {ig_data['id']}")
        print(f"    [OK] New IG_ACCESS_TOKEN: {PAGE_TOKEN[:30]}...")

print("\n" + "=" * 60)
