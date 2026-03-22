#!/usr/bin/env python3
"""
LinkedIn API Poster
===================
Post to LinkedIn using official LinkedIn API (no browser automation)

Agent Skills:
- REST API integration
- OAuth 2.0 authentication
- Media upload support
- Personal & Company posts

Usage:
    python linkedin_api_poster.py [--text "Your post text"] [--image /path/to/image.jpg]
"""

import os
import sys
import logging
import base64
import mimetypes
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
POST_IDEAS_FILE = BASE_DIR / "Post_Ideas.md"
SCREENSHOTS_DIR = BASE_DIR / "Screenshots"
LOGS_DIR = BASE_DIR / "Logs"

# LinkedIn API Configuration
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
PERSON_URN = "urn:li:person:ME"  # Will be resolved from token

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'linkedin_api_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInAPIPoster')


class LinkedInAPIPoster:
    """Post to LinkedIn using official API"""

    def __init__(self, access_token: str, company_urn: str = None):
        self.access_token = access_token
        self.company_urn = company_urn
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.author_urn = None  # Will be resolved on first post (if personal)

    def get_me(self) -> dict:
        """Get current user's LinkedIn URN"""
        url = f"{LINKEDIN_API_BASE}/me"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.author_urn = data.get('id', '')
                logger.info(f"✅ Logged in as: {self.author_urn}")
                print(f"✅ Logged in as: {self.author_urn}")
                return data
            else:
                logger.warning(f"Could not get personal profile ({response.status_code}): {response.text}")
                print("⚠️  Personal profile access not available (common for company tokens)")
                if self.company_urn:
                    print(f"✅ Will post to company: {self.company_urn}")
                return {"id": None}
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach /me endpoint: {e}")
            print(f"⚠️  Network issue checking profile - will try posting anyway")
            if self.company_urn:
                print(f"✅ Will post to company: {self.company_urn}")
            return {"id": None}

    def create_text_post(self, text: str, company_urn: str = None) -> dict:
        """Create a text-only post"""
        # Use company URN if provided, otherwise use personal URN
        target_urn = company_urn or self.company_urn
        
        if target_urn:
            owner = target_urn
            visibility = "PUBLIC"
        else:
            if not self.author_urn:
                self.get_me()
            if not self.author_urn:
                return {"success": False, "error": "No valid author URN available. Provide company_urn or use a token with personal profile access."}
            owner = f"urn:li:person:{self.author_urn}"
            visibility = "PUBLIC"

        url = f"{LINKEDIN_API_BASE}/ugcPosts"
        
        payload = {
            "author": owner,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            post_id = response.json().get('id', '')
            logger.info(f"✅ Text post created: {post_id}")
            return {"success": True, "post_id": post_id, "url": f"https://www.linkedin.com/feed/update/{post_id}"}
        else:
            error_text = response.text
            logger.error(f"Failed to create post: {response.status_code} - {error_text}")
            
            # Check for common permission errors
            if "ACCESS_DENIED" in error_text or "403" in error_text:
                logger.error("Permission denied - check token scopes (w_member_social or w_organization_social required)")
                print("⚠️  Permission Error: Your token needs 'w_member_social' or 'w_organization_social' scope")
                print("📝 Re-authorize at: https://www.linkedin.com/oauth/v2/authorization")
            
            return {"success": False, "error": error_text, "status_code": response.status_code}

    def upload_image(self, image_path: str) -> str:
        """Upload image to LinkedIn and return media artifact URN"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Step 1: Initialize upload
        url = f"{LINKEDIN_API_BASE}/assets"
        
        file_size = os.path.getsize(image_path)
        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
        
        # Use company URN if available, otherwise use personal
        target_urn = self.company_urn or (f"urn:li:person:{self.author_urn}" if self.author_urn else None)
        if not target_urn:
            raise Exception("No valid owner URN. Provide company_urn or authenticate with personal profile.")

        payload = {
            "owner": target_urn,
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalassetRecipe:UPLOAD"
                ],
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:serviceRelationship:AssetRelationship"
                    }
                ],
                "visibility": "PUBLIC"
            }
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
        if response.status_code != 201:
            logger.error(f"Failed to initialize upload: {response.status_code} - {response.text}")
            raise Exception(f"Upload initialization failed: {response.status_code}")

        upload_data = response.json()
        asset_id = upload_data.get('id', '')
        upload_url = upload_data.get('value', {}).get('uploadMechanism', {}).get('com.linkedin.digitalasset.uploadmanual', {}).get('uploadUrl', '')
        
        if not upload_url:
            raise Exception("No upload URL received")

        # Step 2: Upload the actual file
        with open(image_path, 'rb') as f:
            file_data = f.read()

        upload_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': mime_type
        }

        response = requests.put(upload_url, headers=upload_headers, data=file_data, timeout=60)
        
        if response.status_code != 201:
            logger.error(f"Failed to upload image: {response.status_code} - {response.text}")
            raise Exception(f"Image upload failed: {response.status_code}")

        # Step 3: Confirm upload completion
        confirm_url = f"{LINKEDIN_API_BASE}/assets/{asset_id}/confirmUpload"
        confirm_payload = {
            "digitalmediaAsset": asset_id
        }
        
        response = requests.post(confirm_url, headers=self.headers, json=confirm_payload, timeout=30)
        
        if response.status_code != 200:
            logger.warning(f"Upload confirmation warning: {response.status_code}")

        logger.info(f"✅ Image uploaded successfully: {asset_id}")
        return asset_id

    def create_image_post(self, text: str, image_path: str, company_urn: str = None) -> dict:
        """Create a post with an image"""
        try:
            # Upload image first
            print("📤 Uploading image...")
            media_urn = self.upload_image(image_path)
            
            # Determine owner
            target_urn = company_urn or self.company_urn
            
            if target_urn:
                owner = target_urn
                visibility = "PUBLIC"
            else:
                if not self.author_urn:
                    self.get_me()
                if not self.author_urn:
                    return {"success": False, "error": "No valid author URN available. Provide company_urn or use a token with personal profile access."}
                owner = f"urn:li:person:{self.author_urn}"
                visibility = "PUBLIC"

            # Create post with media
            url = f"{LINKEDIN_API_BASE}/ugcPosts"
            
            payload = {
                "author": owner,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": text[:100] + "..." if len(text) > 100 else text
                                },
                                "media": media_urn,
                                "title": {
                                    "text": "LinkedIn Post Image"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 201:
                post_id = response.json().get('id', '')
                logger.info(f"✅ Image post created: {post_id}")
                return {"success": True, "post_id": post_id, "media_urn": media_urn, "url": f"https://www.linkedin.com/feed/update/{post_id}"}
            else:
                logger.error(f"Failed to create image post: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text, "status_code": response.status_code}

        except Exception as e:
            logger.error(f"Error creating image post: {e}")
            return {"success": False, "error": str(e)}

    def create_company_post(self, text: str, company_urn: str, image_path: str = None) -> dict:
        """Create a post on behalf of a company page"""
        if image_path:
            return self.create_image_post(text, image_path, company_urn=company_urn)
        else:
            return self.create_text_post(text, company_urn=company_urn)


def get_post_content(file_path: Path = None) -> str:
    """Get post content from file or generate test content"""
    # Try specified file
    if file_path and file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Remove markdown headers
            content = content.replace('# ', '').replace('## ', '').strip()
            return content[:3000]  # LinkedIn limit

    # Try test_post.md
    test_post = BASE_DIR / "test_post.md"
    if test_post.exists():
        with open(test_post, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            content = content.replace('# ', '').replace('## ', '').strip()
            return content[:3000]

    # Try Post_Ideas.md
    if POST_IDEAS_FILE.exists():
        with open(POST_IDEAS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            posts = content.split('---')
            if posts:
                return posts[0].strip()[:3000]

    # Default test content
    return f"🚀 Test post from AI Employee - LinkedIn API Automation\n\nPosted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#Automation #AI #LinkedIn"


def main():
    """Main entry point"""
    print("=" * 60)
    print("💼 LinkedIn API Poster")
    print("=" * 60)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, default=None,
                       help='Post text (if not provided, will use test_post.md)')
    parser.add_argument('--image', type=str, default=None,
                       help='Path to image file')
    parser.add_argument('--company', action='store_true',
                       help='Post to company page instead of personal profile')
    parser.add_argument('--file', type=str, default=None,
                       help='Path to file containing post text')
    args = parser.parse_args()

    # Get credentials from .env
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip('"')
    company_urn = os.getenv("COMPANY_URN", "").strip('"') or None
    
    # Also check for alternate naming
    if not access_token:
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip('"')
    if not company_urn:
        company_urn = os.getenv("LINKEDIN_COMPANY_URN", os.getenv("COMPANY_URN", "")).strip('"')

    if not access_token:
        logger.error("❌ LinkedIn Access Token not found in .env")
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not set in .env file")
        return 1

    # Ensure directories exist
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Get post text
    post_text = args.text if args.text else get_post_content(Path(args.file) if args.file else None)
    print(f"📝 Post text: {post_text[:100]}...")
    print(f"🖼️  Image: {args.image if args.image else 'None'}")
    print(f"🏢 Post type: {'Company' if args.company else 'Personal'}")

    # Create poster
    try:
        poster = LinkedInAPIPoster(access_token, company_urn)
        
        # Verify authentication
        print("\n🔐 Verifying authentication...")
        poster.get_me()
        if poster.author_urn:
            print(f"✅ Authenticated as: {poster.author_urn}")

        # Create post
        print("\n" + "=" * 40)
        print("📝 Creating Post")
        print("=" * 40)

        if args.company and company_urn:
            print(f"🏢 Posting to company: {company_urn}")
            result = poster.create_company_post(post_text, company_urn, args.image)
        elif args.image:
            print("📤 Creating image post...")
            result = poster.create_image_post(post_text, args.image)
        else:
            print("📝 Creating text post...")
            result = poster.create_text_post(post_text, company_urn if args.company else None)

        # Display results
        print("\n" + "=" * 60)
        print("📊 Results:")
        if result.get('success'):
            print(f"  ✅ Post Status: Success")
            print(f"  🆔 Post ID: {result.get('post_id', 'N/A')}")
            print(f"  🔗 URL: {result.get('url', 'N/A')}")
        else:
            print(f"  ❌ Post Status: Failed")
            print(f"  ⚠️  Error: {result.get('error', 'Unknown error')}")
            if result.get('status_code'):
                print(f"  📋 Status Code: {result.get('status_code')}")
        print("=" * 60)

        return 0 if result.get('success') else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
