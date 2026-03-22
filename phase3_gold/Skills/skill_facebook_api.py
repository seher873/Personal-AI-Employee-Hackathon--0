"""
Agent Skill: Facebook API Poster
Gold Tier - Social Media Integration (API-based)

Uses Facebook Graph API for reliable posting without browser automation.

Usage:
    from skill_facebook_api import FacebookAPISkill
    fb = FacebookAPISkill()
    fb.post("Hello from AI Employee!", "path/to/image.png")
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from config import FB_ACCESS_TOKEN, FB_PAGE_ID


class FacebookAPISkill:
    """Facebook posting skill using Graph API."""

    def __init__(self):
        self.access_token = FB_ACCESS_TOKEN
        self.page_id = FB_PAGE_ID
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.last_post = None
        self.post_count = 0
        self.errors = []

        self._log("FacebookAPISkill initialized")
        self._log(f"Page ID: {self.page_id}")
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
        log_file = os.path.join(self.log_dir, f"facebook_api_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "facebook_api_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")

    def post(self, text, image_path=None):
        """
        Post to Facebook Page using Graph API.

        Args:
            text: Post text content
            image_path: Optional path to image

        Returns:
            dict: Result with success status and details
        """
        self._log(f"Starting post: {text[:50]}...")

        if not self.access_token:
            error_msg = "Facebook Access Token not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        if not self.page_id:
            error_msg = "Facebook Page ID not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        try:
            # Create post on page
            url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
            
            params = {
                'message': text,
                'access_token': self.access_token
            }

            # If image is provided, upload it first
            if image_path and os.path.exists(image_path):
                self._log(f"Uploading image: {image_path}")
                
                # Upload photo to page
                photo_url = f"https://graph.facebook.com/v18.0/{self.page_id}/photos"
                photo_params = {
                    'access_token': self.access_token
                }
                
                with open(image_path, 'rb') as f:
                    photo_files = {'source': f}
                    photo_data = {
                        'published': 'false',
                        'message': text
                    }
                    
                    response = requests.post(
                        photo_url,
                        params=photo_params,
                        files=photo_files,
                        data=photo_data
                    )
                
                if response.status_code == 200:
                    photo_result = response.json()
                    self._log(f"Photo uploaded successfully: {photo_result.get('id')}")
                    return {
                        "success": True,
                        "post_id": photo_result.get('id'),
                        "text": text,
                        "image": image_path
                    }
                else:
                    self._log(f"Photo upload failed: {response.text}")
                    # Fallback to text-only post
                    self._log("Falling back to text-only post")

            # Make the API request
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id', 'unknown')
                
                self._log(f"✅ Post successful! Post ID: {post_id}")
                
                self.last_post = {
                    "text": text,
                    "image": image_path,
                    "timestamp": datetime.now().isoformat(),
                    "platform": "facebook",
                    "post_id": post_id
                }
                self.post_count += 1
                
                self._save_audit("post", {"text": text[:100], "image": image_path, "post_id": post_id}, True)
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "text": text,
                    "image": image_path
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Post failed: {error_msg}")
                
                self.errors.append(error_msg)
                self._save_audit("post", {"text": text[:100], "error": error_msg}, False)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except Exception as e:
            self._log(f"❌ Post error: {e}")
            self.errors.append(str(e))
            self._save_audit("post", {"text": text[:100], "error": str(e)}, False)
            
            return {
                "success": False,
                "error": str(e)
            }

    def get_page_info(self):
        """Get page information."""
        if not self.access_token or not self.page_id:
            return {"error": "Credentials not configured"}
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'name,about,followers_count,likes'
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
            "platform": "Facebook (API)",
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
    print("Facebook API Skill - Test Mode")
    print("=" * 50)

    fb = FacebookAPISkill()
    
    # Get page info
    print("\nPage Info:")
    print(fb.get_page_info())

    # Test post
    result = fb.post("Test post from Facebook API Skill! #AI #Automation")

    print("\nResult:", result)
    print("\nSummary:", fb.generate_summary())
