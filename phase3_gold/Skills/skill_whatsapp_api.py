"""
Agent Skill: WhatsApp Message Sender
Gold Tier - Communication Integration

Uses WhatsApp Business API for sending messages.

Usage:
    from skill_whatsapp_api import WhatsAppAPISkill
    wa = WhatsAppAPISkill()
    wa.send_message("+1234567890", "Hello from AI Employee!")
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from config import WHATSAPP_PHONE, WHATSAPP_API_KEY, WHATSAPP_BUSINESS_ID


class WhatsAppAPISkill:
    """WhatsApp messaging skill using WhatsApp Business API."""

    def __init__(self):
        self.phone_number_id = WHATSAPP_PHONE
        self.api_key = WHATSAPP_API_KEY
        self.business_id = WHATSAPP_BUSINESS_ID
        self.log_dir = "./Logs"
        self.screenshot_dir = "./Screenshots"

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.last_message = None
        self.message_count = 0
        self.errors = []

        self._log("WhatsAppAPISkill initialized")
        self._log(f"Phone Number ID: {self.phone_number_id}")
        self._log(f"API Key present: {'Yes' if self.api_key else 'No'}")
        self._log(f"Business ID: {self.business_id if self.business_id else 'Not set'}")

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
        log_file = os.path.join(self.log_dir, f"whatsapp_api_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def _save_audit(self, action, details, success=True):
        """Save audit log entry."""
        audit_file = os.path.join(self.log_dir, "whatsapp_api_audit.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        }
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")

    def send_message(self, recipient_number, message):
        """
        Send WhatsApp message using WhatsApp Business API.

        Args:
            recipient_number: Recipient's phone number (with country code, e.g., +1234567890)
            message: Message text

        Returns:
            dict: Result with success status and details
        """
        self._log(f"Sending message to {recipient_number}: {message[:50]}...")

        if not self.phone_number_id:
            error_msg = "WhatsApp Phone Number ID not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        if not self.api_key:
            error_msg = "WhatsApp API Key not configured"
            self._log(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        try:
            # WhatsApp Business API endpoint
            url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                
                self._log(f"✅ Message sent successfully! Message ID: {message_id}")
                
                self.last_message = {
                    "recipient": recipient_number,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "platform": "whatsapp",
                    "message_id": message_id
                }
                self.message_count += 1
                
                self._save_audit("send_message", {
                    "recipient": recipient_number,
                    "message": message[:100],
                    "message_id": message_id
                }, True)
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "recipient": recipient_number,
                    "message": message
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Message send failed: {error_msg}")
                
                self.errors.append(error_msg)
                self._save_audit("send_message", {
                    "recipient": recipient_number,
                    "message": message[:100],
                    "error": error_msg
                }, False)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except Exception as e:
            self._log(f"❌ Message error: {e}")
            self.errors.append(str(e))
            self._save_audit("send_message", {
                "recipient": recipient_number,
                "message": message[:100],
                "error": str(e)
            }, False)
            
            return {
                "success": False,
                "error": str(e)
            }

    def send_template_message(self, recipient_number, template_name, template_params=None):
        """
        Send WhatsApp template message.
        
        Template messages are used for sending structured messages
        that have been pre-approved by WhatsApp.

        Args:
            recipient_number: Recipient's phone number
            template_name: Name of the approved template
            template_params: Optional template parameters

        Returns:
            dict: Result with success status and details
        """
        self._log(f"Sending template '{template_name}' to {recipient_number}...")

        if not self.phone_number_id or not self.api_key:
            return {"success": False, "error": "Credentials not configured"}

        try:
            url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en"
                    }
                }
            }
            
            # Add template parameters if provided
            if template_params:
                payload["template"]["components"] = template_params
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                
                self._log(f"✅ Template message sent! Message ID: {message_id}")
                
                self._save_audit("send_template", {
                    "recipient": recipient_number,
                    "template": template_name,
                    "message_id": message_id
                }, True)
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "template": template_name
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Template send failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            self._log(f"❌ Template error: {e}")
            return {"success": False, "error": str(e)}

    def send_media_message(self, recipient_number, media_type, media_url, caption=None):
        """
        Send WhatsApp media message (image, video, document, audio).

        Args:
            recipient_number: Recipient's phone number
            media_type: Type of media ('image', 'video', 'document', 'audio')
            media_url: URL of the media file
            caption: Optional caption for image/video/document

        Returns:
            dict: Result with success status and details
        """
        self._log(f"Sending {media_type} to {recipient_number}...")

        if not self.phone_number_id or not self.api_key:
            return {"success": False, "error": "Credentials not configured"}

        try:
            url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number,
                "type": media_type
            }
            
            # Add media-specific payload
            if media_type == "image":
                payload["image"] = {"link": media_url}
                if caption:
                    payload["image"]["caption"] = caption
            elif media_type == "video":
                payload["video"] = {"link": media_url}
                if caption:
                    payload["video"]["caption"] = caption
            elif media_type == "document":
                payload["document"] = {"link": media_url}
                if caption:
                    payload["document"]["caption"] = caption
            elif media_type == "audio":
                payload["audio"] = {"link": media_url}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                
                self._log(f"✅ Media message sent! Message ID: {message_id}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "media_type": media_type
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                self._log(f"❌ Media send failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            self._log(f"❌ Media error: {e}")
            return {"success": False, "error": str(e)}

    def get_account_info(self):
        """Get WhatsApp Business account information."""
        if not self.phone_number_id or not self.api_key:
            return {"error": "Credentials not configured"}
        
        try:
            url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}"
            params = {
                'fields': 'name,phone_number,quality_rating,verified_name'
            }
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def generate_summary(self):
        """Generate messaging summary."""
        return {
            "platform": "WhatsApp (API)",
            "total_messages": self.message_count,
            "last_message": self.last_message,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }

    def get_stats(self):
        """Get skill statistics."""
        return self.generate_summary()


# CLI usage
if __name__ == "__main__":
    print("WhatsApp API Skill - Test Mode")
    print("=" * 50)

    wa = WhatsAppAPISkill()
    
    # Get account info
    print("\nAccount Info:")
    print(wa.get_account_info())

    # Test message (requires configured credentials)
    if wa.phone_number_id and wa.api_key:
        result = wa.send_message("+1234567890", "Test message from WhatsApp API Skill!")
        print("\nResult:", result)
    else:
        print("\n⚠️ WhatsApp credentials not configured")
        print("Set WHATSAPP_PHONE and WHATSAPP_API_KEY in .env file")
    
    print("\nSummary:", wa.generate_summary())
