"""
Social Media Post Watcher & Publisher
Gold Tier - Unified API-based Posting Script

This script monitors for new posts and publishes to Facebook, Instagram, and WhatsApp.
Uses API-based posting for reliability (no browser automation issues).

Usage:
    python social_post_watcher.py
    
    Or import as module:
    from social_post_watcher import SocialPostWatcher
    watcher = SocialPostWatcher()
    watcher.post_to_all("Hello World!", "image.png")
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    FB_ACCESS_TOKEN, FB_PAGE_ID,
    IG_ID,
    WHATSAPP_PHONE, WHATSAPP_API_KEY
)

# Import API skills
try:
    from Skills.skill_facebook_api import FacebookAPISkill
except ImportError:
    FacebookAPISkill = None

try:
    from Skills.skill_instagram_api import InstagramAPISkill
except ImportError:
    InstagramAPISkill = None

try:
    from Skills.skill_twitter_api import TwitterAPISkill
except ImportError:
    TwitterAPISkill = None

try:
    from Skills.skill_whatsapp_api import WhatsAppAPISkill
except ImportError:
    WhatsAppAPISkill = None


class SocialPostWatcher:
    """Unified social media posting and watching."""

    def __init__(self):
        self.log_dir = "./Logs"
        self.watch_dir = "./Inbox"  # Directory to watch for new posts
        self.post_queue_file = os.path.join(self.log_dir, "post_queue.json")
        
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.watch_dir, exist_ok=True)

        # Initialize skills
        self.fb_skill = FacebookAPISkill() if FacebookAPISkill else None
        self.ig_skill = InstagramAPISkill() if InstagramAPISkill else None
        self.tw_skill = TwitterAPISkill() if TwitterAPISkill else None
        self.wa_skill = WhatsAppAPISkill() if WhatsAppAPISkill else None

        self.stats = {
            "total_posts": 0,
            "facebook_posts": 0,
            "instagram_posts": 0,
            "twitter_posts": 0,
            "whatsapp_messages": 0,
            "errors": 0,
            "last_run": None
        }

        self._log("SocialPostWatcher initialized")
        self._log(f"Facebook API: {'✅' if FB_ACCESS_TOKEN and FB_PAGE_ID else '❌'}")
        self._log(f"Instagram API: {'✅' if IG_ID and FB_ACCESS_TOKEN else '❌'}")
        self._log(f"Twitter API: {'✅' if TwitterAPISkill else '❌'}")
        self._log(f"WhatsApp API: {'✅' if WHATSAPP_PHONE and WHATSAPP_API_KEY else '❌'}")

    def _log(self, message):
        """Internal logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Handle Windows console encoding issues
        try:
            print(log_entry)
        except UnicodeEncodeError:
            # Fallback to ASCII-safe encoding for console
            print(log_entry.encode('cp1252', errors='replace').decode('cp1252'))

        # Also write to file
        log_file = os.path.join(self.log_dir, f"social_watcher_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "social_watcher_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")

    def post_to_facebook(self, text, image_path=None):
        """Post to Facebook."""
        self._log(f"📘 Posting to Facebook: {text[:50]}...")
        
        if not self.fb_skill:
            self._log("❌ Facebook skill not available")
            return {"success": False, "error": "Facebook skill not initialized"}
        
        result = self.fb_skill.post(text, image_path)
        
        if result.get("success"):
            self.stats["facebook_posts"] += 1
            self.stats["total_posts"] += 1
            self._save_audit("facebook_post", {"text": text[:100], "image": image_path}, True)
        else:
            self.stats["errors"] += 1
            self._save_audit("facebook_post", {"text": text[:100], "error": result.get("error")}, False)
        
        return result

    def post_to_instagram(self, caption, image_path):
        """Post to Instagram."""
        self._log(f"📸 Posting to Instagram: {caption[:50]}...")
        
        if not self.ig_skill:
            self._log("❌ Instagram skill not available")
            return {"success": False, "error": "Instagram skill not initialized"}
        
        result = self.ig_skill.post(caption, image_path)
        
        if result.get("success"):
            self.stats["instagram_posts"] += 1
            self.stats["total_posts"] += 1
            self._save_audit("instagram_post", {"caption": caption[:100], "image": image_path}, True)
        else:
            self.stats["errors"] += 1
            self._save_audit("instagram_post", {"caption": caption[:100], "error": result.get("error")}, False)
        
        return result

    def post_to_twitter(self, text, image_path=None):
        """Post to Twitter."""
        self._log(f"[TW] Posting to Twitter: {text[:50]}...")

        if not self.tw_skill:
            self._log("[SKIP] Twitter skill not available")
            return {"success": False, "error": "Twitter skill not initialized"}

        result = self.tw_skill.post(text, image_path)

        if result.get("success"):
            self.stats["twitter_posts"] += 1
            self.stats["total_posts"] += 1
            self._save_audit("twitter_post", {"text": text[:100], "image": image_path}, True)
        else:
            self.stats["errors"] += 1
            self._save_audit("twitter_post", {"text": text[:100], "error": result.get("error")}, False)

        return result

    def send_whatsapp_message(self, recipient, message):
        """Send WhatsApp message."""
        self._log(f"📱 Sending WhatsApp to {recipient}: {message[:50]}...")
        
        if not self.wa_skill:
            self._log("❌ WhatsApp skill not available")
            return {"success": False, "error": "WhatsApp skill not initialized"}
        
        result = self.wa_skill.send_message(recipient, message)
        
        if result.get("success"):
            self.stats["whatsapp_messages"] += 1
            self._save_audit("whatsapp_message", {"recipient": recipient, "message": message[:100]}, True)
        else:
            self.stats["errors"] += 1
            self._save_audit("whatsapp_message", {"recipient": recipient, "error": result.get("error")}, False)
        
        return result

    def post_to_all(self, text, image_path=None, whatsapp_recipients=None):
        """
        Post to all platforms.

        Args:
            text: Post text/caption
            image_path: Optional image path (required for Instagram)
            whatsapp_recipients: List of phone numbers for WhatsApp

        Returns:
            dict: Results from all platforms
        """
        self._log("=" * 60)
        self._log(f"Starting multi-platform post: {text[:50]}...")
        self._log("=" * 60)

        results = {
            "facebook": None,
            "instagram": None,
            "twitter": None,
            "whatsapp": [],
            "timestamp": datetime.now().isoformat()
        }

        # Post to Facebook
        if FB_ACCESS_TOKEN and FB_PAGE_ID:
            results["facebook"] = self.post_to_facebook(text, image_path)
        else:
            self._log("[SKIP] Facebook (credentials not configured)")

        # Post to Instagram (requires image)
        if IG_ID and FB_ACCESS_TOKEN:
            if image_path and os.path.exists(image_path):
                results["instagram"] = self.post_to_instagram(text, image_path)
            else:
                # Use placeholder image from Picsum
                self._log("[INFO] Using placeholder image for Instagram")
                results["instagram"] = self.post_to_instagram(text, "https://picsum.photos/seed/aipost/1080/1080.jpg")
        else:
            self._log("[SKIP] Instagram (credentials not configured)")

        # Post to Twitter
        if self.tw_skill:
            results["twitter"] = self.post_to_twitter(text, image_path)
        else:
            self._log("[SKIP] Twitter (skill not loaded)")

        # Send WhatsApp messages
        if whatsapp_recipients and WHATSAPP_PHONE and WHATSAPP_API_KEY:
            for recipient in whatsapp_recipients:
                wa_result = self.send_whatsapp_message(recipient, text)
                results["whatsapp"].append(wa_result)
        elif whatsapp_recipients:
            self._log("[SKIP] WhatsApp (credentials not configured)")

        self._log("=" * 60)
        self._log("Multi-platform post completed")
        fb_status = "✅" if results["facebook"] and results["facebook"].get("success") else "❌"
        ig_status = "✅" if results["instagram"] and results["instagram"].get("success") else "❌"
        tw_status = "✅" if results["twitter"] and results["twitter"].get("success") else "❌"
        self._log(f"Results: FB={fb_status}, IG={ig_status}, TW={tw_status}, WA={len(results['whatsapp'])} sent")
        self._log("=" * 60)

        return results

    def watch_for_posts(self, interval_seconds=60):
        """
        Watch directory for new posts and publish them.
        
        Monitors the Inbox directory for .post files.
        File format (JSON):
        {
            "text": "Post content",
            "image": "path/to/image.png",
            "platforms": ["facebook", "instagram"],
            "whatsapp_recipients": ["+1234567890"]
        }
        """
        self._log(f"👀 Starting post watcher (checking every {interval_seconds}s)...")
        self._log(f"Watching directory: {self.watch_dir}")

        processed_files = set()

        while True:
            try:
                # Check for .post files
                if os.path.exists(self.watch_dir):
                    post_files = [f for f in os.listdir(self.watch_dir) if f.endswith('.post')]
                    
                    for post_file in post_files:
                        if post_file not in processed_files:
                            self._log(f"📄 Found new post file: {post_file}")
                            self._process_post_file(post_file)
                            processed_files.add(post_file)
                
                self.stats["last_run"] = datetime.now().isoformat()
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self._log("Watcher stopped by user")
                break
            except Exception as e:
                self._log(f"❌ Watcher error: {e}")
                self.stats["errors"] += 1
                time.sleep(interval_seconds)

    def _process_post_file(self, filename):
        """Process a single post file."""
        try:
            file_path = os.path.join(self.watch_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                post_data = json.load(f)
            
            text = post_data.get('text', '')
            image = post_data.get('image')
            platforms = post_data.get('platforms', ['facebook'])
            whatsapp_recipients = post_data.get('whatsapp_recipients', [])
            
            if not text:
                self._log(f"❌ Post file {filename} has no text")
                return
            
            self._log(f"Processing post: {text[:50]}...")
            
            # Post to selected platforms
            if 'facebook' in platforms:
                self.post_to_facebook(text, image)
            
            if 'instagram' in platforms:
                if image:
                    self.post_to_instagram(text, image)
                else:
                    self._log("⚠️ Skipping Instagram (image required)")
            
            if whatsapp_recipients:
                for recipient in whatsapp_recipients:
                    self.send_whatsapp_message(recipient, text)
            
            # Mark file as processed
            processed_path = file_path.replace('.post', '.processed')
            os.rename(file_path, processed_path)
            self._log(f"✅ Post processed: {filename}")
            
        except Exception as e:
            self._log(f"❌ Error processing {filename}: {e}")
            self.stats["errors"] += 1

    def get_stats(self):
        """Get watcher statistics."""
        return self.stats

    def print_stats(self):
        """Print statistics."""
        print("\n" + "=" * 60)
        print("Social Post Watcher Statistics")
        print("=" * 60)
        print(f"Total Posts: {self.stats['total_posts']}")
        print(f"  - Facebook: {self.stats['facebook_posts']}")
        print(f"  - Instagram: {self.stats['instagram_posts']}")
        print(f"  - WhatsApp Messages: {self.stats['whatsapp_messages']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Last Run: {self.stats['last_run'] or 'Never'}")
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media Post Watcher & Publisher')
    parser.add_argument('--watch', action='store_true', help='Run in watch mode (continuous)')
    parser.add_argument('--interval', type=int, default=60, help='Watch interval in seconds')
    parser.add_argument('--post', type=str, help='Post text')
    parser.add_argument('--image', type=str, help='Image path')
    parser.add_argument('--platforms', type=str, nargs='+', 
                        choices=['facebook', 'instagram', 'whatsapp'],
                        help='Platforms to post to')
    parser.add_argument('--whatsapp-to', type=str, nargs='+', help='WhatsApp recipients')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    watcher = SocialPostWatcher()
    
    if args.stats:
        watcher.print_stats()
        return
    
    if args.watch:
        # Watch mode
        watcher.watch_for_posts(args.interval)
    elif args.post:
        # One-time post
        platforms = args.platforms or ['facebook']
        image = args.image
        whatsapp_to = args.whatsapp_to or []
        
        # If Instagram is selected but no image, warn
        if 'instagram' in platforms and not image:
            print("⚠️ Instagram requires an image. Skipping Instagram.")
            platforms.remove('instagram')
        
        watcher.post_to_all(args.post, image, whatsapp_to)
        watcher.print_stats()
    else:
        # No arguments - show help
        parser.print_help()


if __name__ == "__main__":
    main()
