"""
Check WhatsApp Messages via WhatsApp Business API
Uses Meta Graph API to read incoming messages
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WHATSAPP_PHONE, WHATSAPP_API_KEY, WHATSAPP_BUSINESS_ID

# Inbox directory
INBOX_DIR = "./Inbox"
LOGS_DIR = "./Logs"
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class WhatsAppAPIChecker:
    """Check WhatsApp messages using WhatsApp Business API."""

    def __init__(self):
        self.phone_number_id = WHATSAPP_PHONE
        self.api_key = WHATSAPP_API_KEY
        self.business_id = WHATSAPP_BUSINESS_ID
        self.base_url = "https://graph.facebook.com/v17.0"
        
        print("=" * 60)
        print("WhatsApp API Message Checker")
        print("=" * 60)
        print(f"\nPhone Number ID: {self.phone_number_id if self.phone_number_id else 'NOT SET'}")
        print(f"API Key Present: {'Yes' if self.api_key else 'NO'}")
        print(f"Business ID: {self.business_id if self.business_id else 'NOT SET'}")
        print("=" * 60)

    def _log(self, message):
        """Log message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def check_messages(self, limit=10):
        """
        Check recent messages from WhatsApp API.
        
        Note: WhatsApp Business API requires webhook setup for receiving messages.
        This method checks the conversation history via the API.
        """
        self._log("\n[*] Checking WhatsApp messages via API...")
        
        if not self.phone_number_id:
            print("\n[ERROR] WhatsApp Phone Number ID not configured!")
            print("Set WHATSAPP_PHONE in .env file")
            return []
        
        if not self.api_key:
            print("\n[ERROR] WhatsApp API Key not configured!")
            print("Set WHATSAPP_API_KEY in .env file")
            return []
        
        try:
            # Get conversations/messages
            # Note: WhatsApp API uses conversations endpoint
            url = f"{self.base_url}/{self.phone_number_id}/conversations"
            
            params = {
                'limit': limit,
                'fields': 'messages,contacts'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            self._log(f"[*] API Request: GET {url}")
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            self._log(f"[*] API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self._log(f"[OK] API Response received")
                
                conversations = data.get('data', [])
                
                if conversations:
                    print(f"\n[OK] Found {len(conversations)} conversation(s)!\n")
                    print("=" * 60)
                    
                    messages_found = []
                    
                    for conv in conversations:
                        conv_id = conv.get('id', 'Unknown')
                        messages = conv.get('messages', [])
                        contacts = data.get('contacts', [])
                        
                        # Get contact info
                        contact_wa_id = conv.get('contacts', [{}])[0].get('wa_id', 'Unknown')
                        contact_name = "Unknown"
                        
                        for contact in contacts:
                            if contact.get('wa_id') == contact_wa_id:
                                contact_name = contact.get('profile', {}).get('name', contact_w_id)
                                break
                        
                        print(f"\n[Conversation: {contact_name} ({contact_wa_id})]")
                        print(f"  Conversation ID: {conv_id}")
                        
                        for msg in messages[-5:]:  # Last 5 messages per conversation
                            msg_id = msg.get('id', 'N/A')
                            msg_from = msg.get('from', 'Unknown')
                            msg_text = msg.get('text', {}).get('body', 'N/A')
                            msg_timestamp = msg.get('timestamp', 'N/A')
                            
                            # Convert timestamp to readable format
                            if msg_timestamp.isdigit():
                                dt = datetime.fromtimestamp(int(msg_timestamp) / 1000)
                                msg_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            direction = "IN" if msg_from == contact_wa_id else "OUT"
                            
                            print(f"  [{direction}] {msg_timestamp}: {msg_text[:80]}")
                            
                            messages_found.append({
                                'from': contact_name,
                                'phone': contact_wa_id,
                                'message': msg_text,
                                'timestamp': msg_timestamp,
                                'direction': direction
                            })
                    
                    print("\n" + "=" * 60)
                    print(f"\n[OK] Total: {len(messages_found)} message(s) found")
                    
                    # Save to inbox
                    if messages_found:
                        self._save_to_inbox(messages_found)
                    
                    return messages_found
                else:
                    print("\n[!] No conversations found")
                    print("    - Make sure your WhatsApp Business account has messages")
                    print("    - Check if API has proper permissions")
                    return []
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                print(f"\n[ERROR] API request failed: {error_msg}")
                
                # Show error details
                if 'error' in error_data:
                    error_info = error_data['error']
                    print(f"  Type: {error_info.get('type', 'N/A')}")
                    print(f"  Code: {error_info.get('code', 'N/A')}")
                    print(f"  Message: {error_info.get('message', 'N/A')}")
                
                return []
                
        except requests.exceptions.Timeout:
            print("\n[ERROR] API request timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] API request failed: {e}")
            return []
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _save_to_inbox(self, messages):
        """Save messages to Inbox folder."""
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_whatsapp_api.md"
        filepath = os.path.join(INBOX_DIR, filename)
        
        content = f"""---
created: {timestamp.isoformat()}
source: whatsapp_api
total_messages: {len(messages)}
status: pending
---

# WhatsApp Messages (API Import)

## Messages

"""
        for msg in messages:
            content += f"""
### From: {msg['from']} ({msg['phone']})
- **Time:** {msg['timestamp']}
- **Direction:** {msg['direction']}
- **Message:** {msg['message']}

---
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"[INBOX] Saved: {filename}")
        except Exception as e:
            self._log(f"[ERROR] Failed to save: {e}")

    def get_account_info(self):
        """Get WhatsApp Business account info."""
        if not self.phone_number_id or not self.api_key:
            return {"error": "Credentials not configured"}
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            params = {
                'fields': 'name,phone_number,quality_rating,verified_name,message_template_namespace'
            }
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "details": response.text}
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main function."""
    checker = WhatsAppAPIChecker()
    
    # Get account info first
    print("\n[*] Getting account info...")
    account_info = checker.get_account_info()
    print(f"\nAccount Info: {json.dumps(account_info, indent=2)}")
    
    # Check messages
    messages = checker.check_messages(limit=10)
    
    print("\n" + "=" * 60)
    print("[OK] Done!")


if __name__ == "__main__":
    main()
