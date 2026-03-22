#!/usr/bin/env python3
"""
Guide to get a proper token with Instagram permissions
"""

print("INSTAGRAM API POSTING - PROPER TOKEN SETUP")
print("=" * 70)

print("\nYour current token is valid but missing required permissions.")
print("Missing permissions for Instagram API posting:")
print("  - instagram_basic")
print("  - instagram_content_publish")

print("\nTo get a token with the required permissions:")
print("1. Go to Facebook Developers: https://developers.facebook.com/")
print("2. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/")
print("3. Select your app")
print("4. Click 'Get Token' -> 'Get User Access Token'")
print("5. Select these EXACT permissions:")
print("   - ads_management")
print("   - instagram_basic")
print("   - instagram_content_publish")
print("   - pages_show_list")
print("   - pages_read_engagement")
print("   - business_management")
print("6. Click 'Continue' -> 'Done'")
print("7. Copy the new token and replace the FB_ACCESS_TOKEN in your .env file")

print("\nIMPORTANT: Make sure you have:")
print("1. A Facebook Page (create one if needed)")
print("2. An Instagram Business Account connected to that Facebook Page")
print("   (This is done in your Facebook Page settings -> Instagram)")

print("\nAfter getting the proper token:")
print("1. Update your .env file with the new token")
print("2. Find your Instagram Business Account ID using one of these methods:")
print("   a) In Graph API Explorer: GET /me/accounts?fields=instagram_business_account")
print("   b) Business Manager: https://business.facebook.com/creatorstudio/")
print("3. Update IG_ID in your .env file")
print("4. Then run: python -m Skills.skill_instagram_api")

print("\nAlternatively, if you want immediate posting capability without setting up API,")
print("you can use the browser-based approach, but you'll need to update selectors to")
print("work with Instagram's current interface.")

print("=" * 70)