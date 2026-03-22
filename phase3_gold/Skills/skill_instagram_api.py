"""
Agent Skill: Instagram API Poster
Gold Tier - Social Media Integration (API-based)

Uses Instagram Graph API for reliable posting without browser automation.

Usage:
    from skill_instagram_api import InstagramAPISkill
    ig = InstagramAPISkill()
    ig.post("Hello from AI Employee!", "path/to/image.png")
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from config import FB_ACCESS_TOKEN, IG_ID

# Import Imgur uploader
try:
    from imgur_uploader import upload_to_imgur
    IMGUR_AVAILABLE = True
except ImportError:
    IMGUR_AVAILABLE = False


class InstagramAPISkill:
    """Instagram posting skill using Graph API."""

    def __init__(self):
        self.access_token = FB_ACCESS_TOKEN  # Instagram uses FB access token
        self.ig_id = IG_ID
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.last_post = None
        self.post_count = 0
        self.errors = []

        self._log("InstagramAPISkill initialized")
        self._log(f"Instagram ID: {self.ig_id}")
        self._log(f"Token present: {'Yes' if self.access_token else 'No'}")

    def _log(self, message):
        """Internal logging."""
        import sys
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Handle Windows console encoding
        try:
            print(log_entry)
        except UnicodeEncodeError:
            sys.stdout.reconfigure(encoding='cp1252', errors='replace')
            print(log_entry.encode('cp1252', errors='replace').decode('cp1252'))

        # Also write to file
        log_file = os.path.join(self.log_dir, f"instagram_api_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "instagram_api_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")

    def post(self, caption, image_path=None):
        """
        Post to Instagram using Graph API.

        Instagram API requires:
        1. Create a container (post with image)
        2. Publish the container

        Args:
            caption: Post caption
            image_path: Path to image (required for Instagram)

        Returns:
            dict: Result with success status and details
        """
        self._log(f"Starting post: {caption[:50]}...")

        if not self.access_token:
            error_msg = "Facebook Access Token not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        if not self.ig_id:
            error_msg = "Instagram ID not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        if not image_path:
            error_msg = "Image path is required for Instagram posts"
            self._log(f"[ERROR] {error_msg}")
            return {"success": False, "error": error_msg}

        try:
            # Check if it's a URL (starts with http)
            if image_path.startswith('http://') or image_path.startswith('https://'):
                # It's already a URL, use with the standard approach
                image_url = image_path
                self._log(f"[OK] Using online image URL: {image_url[:50]}...")

                # Step 1: Create a container with URL
                self._log("Creating container...")
                self._log(f"Using image URL: {image_url[:60]}...")

                container_url = f"https://graph.facebook.com/v18.0/{self.ig_id}/media"
                container_params = {
                    'image_url': image_url,
                    'caption': caption,
                    'access_token': self.access_token
                }

                response = requests.post(container_url, params=container_params)
            else:
                # For local files, we need to upload directly
                if not os.path.exists(image_path):
                    error_msg = f"Image file not found: {image_path}"
                    self._log(f"[ERROR] {error_msg}")
                    return {"success": False, "error": error_msg}

                self._log(f"[INFO] Uploading local image file directly: {image_path}")

                # For local files, upload directly to the media endpoint
                container_url = f"https://graph.facebook.com/v18.0/{self.ig_id}/media"
                container_data = {
                    'caption': caption,
                    'access_token': self.access_token
                }

                with open(image_path, 'rb') as f:
                    files = {'image_url': (os.path.basename(image_path), f, 'image/jpeg')}
                    response = requests.post(container_url, data=container_data, files=files)

            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Container creation failed: {error_msg}")
                return {"success": False, "error": error_msg}

            container_result = response.json()
            creation_id = container_result.get('id')
            self._log(f"Container created: {creation_id}")

            # Step 2: Wait for container to be ready
            self._log("Waiting for container to be ready...")
            time.sleep(5)  # Instagram needs time to process

            # Step 3: Publish the container
            self._log("Publishing container...")

            publish_url = f"https://graph.facebook.com/v18.0/{self.ig_id}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }

            response = requests.post(publish_url, params=publish_params)

            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id', 'unknown')

                self._log(f"✅ Post successful! Post ID: {post_id}")

                self.last_post = {
                    "caption": caption,
                    "image": image_path,
                    "timestamp": datetime.now().isoformat(),
                    "platform": "instagram",
                    "post_id": post_id
                }
                self.post_count += 1

                self._save_audit("post", {"caption": caption[:100], "image": image_path, "post_id": post_id}, True)

                return {
                    "success": True,
                    "post_id": post_id,
                    "caption": caption,
                    "image": image_path
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Publish failed: {error_msg}")

                self.errors.append(error_msg)
                self._save_audit("post", {"caption": caption[:100], "error": error_msg}, False)

                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except Exception as e:
            self._log(f"❌ Post error: {e}")
            self.errors.append(str(e))
            self._save_audit("post", {"caption": caption[:100], "error": str(e)}, False)

            return {
                "success": False,
                "error": str(e)
            }

    def _get_image_url(self, image_path):
        """
        Get publicly accessible image URL.

        Priority:
        1. If already URL (http/https) → return as-is
        2. If local file → try to upload to Imgur or return file URL as fallback
        """
        # If it's already a URL, return it
        if image_path.startswith('http://') or image_path.startswith('https://'):
            self._log(f"[OK] Using online URL: {image_path[:60]}...")
            return image_path

        # For local files, try to upload to Imgur first
        if IMGUR_AVAILABLE:
            self._log(f"[INFO] Uploading local image to Imgur: {image_path}")
            try:
                from imgur_uploader import upload_to_imgur
                result = upload_to_imgur(image_path)
                if result.get("success"):
                    imgur_url = result["url"]
                    self._log(f"[OK] Uploaded to Imgur: {imgur_url[:60]}...")
                    return imgur_url
                else:
                    self._log(f"[ERROR] Imgur upload failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                self._log(f"[ERROR] Imgur upload failed: {e}")

        # Fallback: try to make a POST request with local file directly to Instagram API
        # This approach uploads the file directly instead of using a URL
        self._log(f"[INFO] Local file detected, will upload directly")
        return image_path  # Return the local path to be handled specially later

    def get_account_info(self):
        """Get Instagram Business account information."""
        if not self.access_token or not self.ig_id:
            return {"error": "Credentials not configured"}
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.ig_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'username,biography,followers_count,follows_count,media_count'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def generate_summary(self):
        """Generate posting summary."""
        return {
            "platform": "Instagram (API)",
            "total_posts": self.post_count,
            "last_post": self.last_post,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }

    def get_stats(self):
        """Get skill statistics."""
        return self.generate_summary()


# CLI usage
if __name__ == "__main__":
    print("Instagram API Skill - Test Mode")
    print("=" * 50)

    ig = InstagramAPISkill()
    
    # Get account info
    print("\nAccount Info:")
    print(ig.get_account_info())

    # Test post (requires image)
    import os
    test_image = os.path.join(os.path.dirname(__file__), "post_image.png")
    
    if os.path.exists(test_image):
        result = ig.post("Test post from Instagram API Skill! #AI #Automation", test_image)
        print("\nResult:", result)
    else:
        print(f"\n⚠️ Test image not found: {test_image}")
        print("Create a test image first or provide a valid image path")
    
    print("\nSummary:", ig.generate_summary())
