"""
Agent Skill: Twitter/X API Poster
Gold Tier - Social Media Integration (API-based)

Uses Twitter API v2 for reliable posting without browser automation.

Usage:
    from skill_twitter_api import TwitterAPISkill
    twitter = TwitterAPISkill()
    twitter.post("Hello from AI Employee!", "path/to/image.png")
"""

import os
import sys
import json
import requests
import base64
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)


class TwitterAPISkill:
    """Twitter posting skill using Twitter API v2."""
    
    def __init__(self):
        self.api_key = TWITTER_API_KEY
        self.api_secret = TWITTER_API_SECRET
        self.access_token = TWITTER_ACCESS_TOKEN
        self.access_token_secret = TWITTER_ACCESS_TOKEN_SECRET
        self.bearer_token = TWITTER_BEARER_TOKEN
        
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"
        
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.last_post = None
        self.post_count = 0
        self.errors = []
        
        self._log("TwitterAPISkill initialized")
        self._log(f"API Key present: {'Yes' if self.api_key else 'No'}")
        self._log(f"Access Token present: {'Yes' if self.access_token else 'No'}")
        self._log(f"Bearer Token present: {'Yes' if self.bearer_token else 'No'}")
    
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
        log_file = os.path.join(self.log_dir, f"twitter_api_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "twitter_api_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_oauth1_params(self):
        """Get OAuth 1.0a parameters for API calls."""
        import oauthlib
        from requests_oauthlib import OAuth1Session
        
        return OAuth1Session(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret
        )
    
    def post(self, text, image_path=None):
        """
        Post to Twitter using API v2.
        
        Args:
            text: Tweet text (max 280 characters)
            image_path: Optional path to image
        
        Returns:
            dict: Result with success status and tweet ID
        """
        self._log(f"Starting tweet: {text[:50]}...")
        
        # Check credentials
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            error_msg = "Twitter API credentials not configured"
            self._log(f"[ERROR] {error_msg}")
            self._log("[INFO] Get credentials from: https://developer.twitter.com/")
            return {"success": False, "error": error_msg}
        
        try:
            # Step 1: Upload media (if image provided)
            media_id = None
            if image_path and os.path.exists(image_path):
                self._log(f"Uploading image: {image_path}")
                media_id = self._upload_media(image_path)
                
                if not media_id:
                    self._log("[WARN] Media upload failed, posting text only")
            
            # Step 2: Create tweet
            self._log("Creating tweet...")
            
            oauth = self._get_oauth1_params()
            
            tweet_data = {"text": text}
            
            if media_id:
                tweet_data["media"] = {"media_ids": [media_id]}
            
            response = oauth.post(
                "https://api.twitter.com/2/tweets",
                json=tweet_data
            )
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get("data", {}).get("id")
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                self._log(f"[OK] Tweet posted successfully!")
                self._log(f"    Tweet ID: {tweet_id}")
                self._log(f"    URL: {tweet_url}")
                
                self.post_count += 1
                self.last_post = tweet_id
                
                self._save_audit("twitter_post", {"text": text[:100], "tweet_id": tweet_id}, True)
                
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "text": text
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                self._log(f"[ERROR] Tweet failed: {error_msg}")
                
                self._save_audit("twitter_post", {"text": text[:100], "error": error_msg}, False)
                
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._log(f"[ERROR] {error_msg}")
            self._save_audit("twitter_post", {"text": text[:100], "error": str(e)}, False)
            
            return {"success": False, "error": error_msg}
    
    def _upload_media(self, image_path):
        """
        Upload media to Twitter.
        
        Returns:
            str: Media ID string or None
        """
        try:
            oauth = self._get_oauth1_params()
            
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Upload to media endpoint
            response = oauth.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                files={"media": image_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                media_id = result.get("media_id_string")
                self._log(f"[OK] Media uploaded: {media_id}")
                return media_id
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                self._log(f"[ERROR] Media upload failed: {error_msg}")
                return None
                
        except Exception as e:
            self._log(f"[ERROR] Media upload exception: {e}")
            return None
    
    def get_account_info(self):
        """Get Twitter account information."""
        try:
            oauth = self._get_oauth1_params()
            
            response = oauth.get(
                "https://api.twitter.com/2/users/me",
                params={"user.fields": "name,username,description,public_metrics,verified"}
            )
            
            if response.status_code == 200:
                result = response.json()
                user_data = result.get("data", {})
                
                self._log(f"[INFO] Account: @{user_data.get('username')}")
                self._log(f"    Name: {user_data.get('name')}")
                self._log(f"    Followers: {user_data.get('public_metrics', {}).get('followers_count', 0)}")
                
                return {
                    "success": True,
                    "username": user_data.get("username"),
                    "name": user_data.get("name"),
                    "followers": user_data.get("public_metrics", {}).get("followers_count")
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_thread(self, tweets):
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
        
        Returns:
            dict: Result with tweet IDs
        """
        self._log(f"Posting thread with {len(tweets)} tweets...")
        
        tweet_ids = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            # Add thread indicator
            if len(tweets) > 1:
                tweet_text = f"({i+1}/{len(tweets)}) {tweet_text}"
            
            # Post tweet
            result = self.post(tweet_text)
            
            if result.get("success"):
                tweet_id = result.get("tweet_id")
                tweet_ids.append(tweet_id)
                
                # Reply to previous tweet (for thread)
                if previous_tweet_id and i > 0:
                    reply_result = self._reply_to_tweet(previous_tweet_id, tweet_text)
                    if reply_result.get("success"):
                        tweet_ids[-1] = reply_result.get("tweet_id")
                
                previous_tweet_id = tweet_ids[-1]
            else:
                self._log(f"[ERROR] Thread tweet {i+1} failed: {result.get('error')}")
        
        return {
            "success": len(tweet_ids) == len(tweets),
            "tweet_ids": tweet_ids,
            "posted": len(tweet_ids),
            "total": len(tweets)
        }
    
    def _reply_to_tweet(self, tweet_id, text):
        """Reply to a specific tweet."""
        try:
            oauth = self._get_oauth1_params()
            
            response = oauth.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": text,
                    "reply": {"in_reply_to_tweet_id": tweet_id}
                }
            )
            
            if response.status_code == 201:
                result = response.json()
                reply_id = result.get("data", {}).get("id")
                self._log(f"[OK] Reply posted: {reply_id}")
                return {"success": True, "tweet_id": reply_id}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Twitter API Skill - Test")
    print("=" * 60)
    
    twitter = TwitterAPISkill()
    
    # Test account info
    print("\n[TEST] Getting account info...")
    account = twitter.get_account_info()
    print(account)
    
    # Test post
    print("\n[TEST] Posting test tweet...")
    result = twitter.post("Test from AI Employee! 🤖 #AI #Hackathon")
    print(result)
