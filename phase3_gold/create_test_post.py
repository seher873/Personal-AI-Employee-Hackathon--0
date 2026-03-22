#!/usr/bin/env python3
"""
Create a test post using the Instagram API with the provided token
"""
import requests
import json
from config import FB_ACCESS_TOKEN
import os

def test_instagram_post():
    print("Testing Instagram API posting...")
    print(f"Using token with permissions: instagram_basic, instagram_content_publish")
    print()

    # Validate that we have the required files
    if not os.path.exists('post_image.png'):
        print("ERROR: post_image.png not found!")
        print("Create an image named 'post_image.png' in the root directory first.")
        return

    # The issue is that we need to know the Instagram Business Account ID
    # Let's try to find it using the user's pages
    print("Looking for connected Instagram Business Account...")

    try:
        # Try to access user's pages again, but with the right approach
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={FB_ACCESS_TOKEN}&fields=name,instagram_business_account,access_token"
        pages_response = requests.get(pages_url)

        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            pages = pages_data.get('data', [])

            if not pages:
                print("No Facebook Pages found!")
                print("\nSOLUTION:")
                print("1. Go to https://www.facebook.com/pages/creation/")
                print("2. Create a new Facebook Page (any category)")
                print("3. Connect your Instagram Business Account to the Facebook Page")
                print("   - Go to your Facebook Page settings")
                print("   - Find 'Instagram' section")
                print("   - Click 'Connect Account' and follow instructions")
                print("4. Once connected, run this script again")
                return
            else:
                print(f"Found {len(pages)} Facebook Page(s):")
                for i, page in enumerate(pages):
                    print(f"  {i+1}. {page['name']} (ID: {page['id']})")

                    # Check if this page has Instagram connected
                    ig_account = page.get('instagram_business_account')
                    if ig_account:
                        ig_id = ig_account['id']
                        print(f"     -> Instagram Business Account ID: {ig_id}")
                        print(f"     -> Instagram Username: {ig_account.get('username', 'N/A')}")

                        # NOW we can try to make a post!
                        print(f"\nAttempting to create a test post...")
                        print(f"Using Instagram ID: {ig_id}")

                        # Update the .env file with this IG ID
                        update_env_file(ig_id)

                        # Try to create a media object
                        caption = "Test post from AI Employee Vault! #AI #Automation #Testing"
                        image_url = f"file://{os.path.abspath('post_image.png')}"

                        # Step 1: Create a container
                        container_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
                        container_data = {
                            'image_url': image_url,
                            'caption': caption,
                            'access_token': FB_ACCESS_TOKEN
                        }

                        print(f"Creating media container...")
                        container_response = requests.post(container_url, data=container_data)

                        if container_response.status_code == 200:
                            container_result = container_response.json()
                            creation_id = container_result.get('id')
                            print(f"Container created successfully! ID: {creation_id}")

                            # Step 2: Publish the container
                            print(f"Publishing container...")
                            publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
                            publish_data = {
                                'creation_id': creation_id,
                                'access_token': FB_ACCESS_TOKEN
                            }

                            publish_response = requests.post(publish_url, data=publish_data)

                            if publish_response.status_code == 200:
                                publish_result = publish_response.json()
                                post_id = publish_result.get('id')
                                print(f"SUCCESS! Post published to Instagram!")
                                print(f"Post ID: {post_id}")
                                print(f"Caption: {caption}")
                            else:
                                print(f"Publish failed: {publish_response.status_code} - {publish_response.text}")
                        else:
                            print(f"Container creation failed: {container_response.status_code} - {container_response.text}")
                            print("Note: Direct file:// URLs might not work. Try uploading image to a public URL first.")

                    else:
                        print(f"     -> No Instagram Business Account connected")

        else:
            print(f"Could not access pages: {pages_response.status_code} - {pages_response.text}")

    except Exception as e:
        print(f"Error during process: {e}")
        import traceback
        traceback.print_exc()

def update_env_file(ig_id):
    """Update the .env file with the found IG ID"""
    # Read the current .env file
    with open('.env', 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace the IG_ID line
    import re
    updated_content = re.sub(
        r'IG_ID=.*$',
        f'IG_ID={ig_id}',
        content,
        flags=re.MULTILINE
    )

    # Write back to the .env file
    with open('.env', 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"Updated IG_ID in .env file to: {ig_id}")

if __name__ == "__main__":
    test_instagram_post()