#!/usr/bin/env python3
"""
LinkedIn API Skill - Gold Tier
==============================
Post to LinkedIn using Official API (NOT browser automation)
Uses OAuth 2.0 tokens from .env file

Setup Guide:
1. Create LinkedIn App: https://www.linkedin.com/developers/apps
2. Get Client ID, Client Secret, Access Token
3. Add credentials to .env file (already done)
4. Run this skill

API Docs: https://learn.microsoft.com/en-us/linkedin/consumer/integrations
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()


class LinkedInAPIClient:
    """LinkedIn API Client for posting and management"""

    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.company_urn = os.getenv("COMPANY_URN", "")

        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        self._validate_credentials()

    def _validate_credentials(self):
        """Validate that credentials are loaded"""
        if not self.client_id:
            raise ValueError("LINKEDIN_CLIENT_ID not found in .env")
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not found in .env")
        print("[OK] LinkedIn API credentials loaded")

    def get_user_profile(self):
        """Get current user's profile information"""
        url = f"{self.base_url}/me"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_company_page(self):
        """Get company page information"""
        if not self.company_urn:
            print("COMPANY_URN not set in .env")
            return None

        url = f"{self.base_url}/organizations/{self.company_urn.split(':')[-1]}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def post_text(self, text: str, company: bool = False):
        """
        Post text update to LinkedIn

        Args:
            text: Post content
            company: If True, post to company page; else personal profile
        """
        # Determine target URN
        if company and self.company_urn:
            target_urn = self.company_urn
            post_type = "company"
        else:
            # Get personal URN
            profile = self.get_user_profile()
            if profile:
                target_urn = f"urn:li:person:{profile['id']}"
            else:
                target_urn = "urn:li:person:YOUR_ID"  # Fallback
            post_type = "personal"

        # Create post payload
        payload = {
            "author": target_urn,
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
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # API endpoint
        url = f"{self.base_url}/ugcPosts"

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 201:
            result = response.json()
            post_id = result.get('id', 'unknown')
            print(f"[OK] Posted successfully to {post_type} LinkedIn!")
            print(f"  Post ID: {post_id}")
            return {
                "success": True,
                "post_id": post_id,
                "type": post_type,
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"[ERROR] Post failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }

    def post_with_image(self, text: str, image_path: str, company: bool = False):
        """
        Post with image to LinkedIn

        Args:
            text: Post content
            image_path: Path to image file
            company: If True, post to company page
        """
        # Step 1: Upload image to get URL
        image_url = self._upload_image(image_path)
        if not image_url:
            return {"success": False, "error": "Image upload failed"}

        # Step 2: Create post with image
        if company and self.company_urn:
            target_urn = self.company_urn
            post_type = "company"
        else:
            profile = self.get_user_profile()
            target_urn = f"urn:li:person:{profile['id']}" if profile else "urn:li:person:YOUR_ID"
            post_type = "personal"

        payload = {
            "author": target_urn,
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
                                "text": text
                            },
                            "originalUrl": image_url,
                            "title": {
                                "text": "LinkedIn Post Image"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        url = f"{self.base_url}/ugcPosts"
        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 201:
            result = response.json()
            print(f"[OK] Posted with image successfully to {post_type} LinkedIn!")
            return {
                "success": True,
                "post_id": result.get('id'),
                "type": post_type,
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"[ERROR] Post failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }

    def _upload_image(self, image_path: str):
        """
        Upload image to LinkedIn and get URL
        Simplified version - returns placeholder URL
        For production, implement LinkedIn's upload API
        """
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        # Note: LinkedIn image upload requires multipart upload
        # This is a simplified version - for demo purposes
        # In production, use: https://learn.microsoft.com/en-us/linkedin/shared/media-kit

        print(f"  Image path: {image_path}")
        print(f"  Note: Full image upload requires LinkedIn's multipart API")
        return "https://via.placeholder.com/1200x627.png?text=LinkedIn+Post"

    def test_connection(self):
        """Test API connection"""
        print("Testing LinkedIn API connection...")
        profile = self.get_user_profile()
        if profile:
            print(f"✓ Connected as: {profile.get('localizedFirstName', 'Unknown')} {profile.get('localizedLastName', 'User')}")
            return True
        else:
            print("✗ Connection failed")
            return False


def main():
    """Test LinkedIn API Skill"""
    print("=" * 60)
    print("LinkedIn API Skill - Test")
    print("=" * 60)

    try:
        client = LinkedInAPIClient()

        # Test connection
        print("\n1. Testing connection...")
        client.test_connection()

        # Get company info
        print("\n2. Getting company page...")
        company = client.get_company_page()
        if company:
            print(f"   Company: {company.get('localizedName', 'Unknown')}")

        # Post test message
        print("\n3. Posting test message...")
        result = client.post_text(
            text="Hello from AI Employee! Testing LinkedIn API integration. #AI #Automation #LinkedInAPI",
            company=False
        )

        if result.get('success'):
            print("\n✓ SUCCESS! Post created.")
        else:
            print(f"\n✗ Failed: {result.get('error')}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check .env file has LINKEDIN_* credentials")
        print("2. Verify access token is valid (not expired)")
        print("3. Ensure LinkedIn app has required permissions")


if __name__ == '__main__':
    main()
