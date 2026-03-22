#!/usr/bin/env python3
"""
Simple LinkedIn OAuth Server
Captures authorization code and exchanges for token
"""

import os
import sys
import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import webbrowser
from dotenv import load_dotenv

load_dotenv()

PORT = 8081
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
REDIRECT_URI = f"http://localhost:{PORT}"

print("=" * 60)
print("🔑 LinkedIn Token Generator")
print("=" * 60)
print(f"Client ID: {CLIENT_ID}")
print(f"Redirect URI: {REDIRECT_URI}")

# Generate auth URL
auth_params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'w_member_social'
}
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(auth_params)}"

print(f"\n📝 Step 1: Authorize")
print(f"Opening: {auth_url[:100]}...")

# Open browser
webbrowser.open(auth_url)

# Server to capture code
captured_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code
        if self.path.startswith('/?code=') or self.path.startswith('/?error='):
            params = urllib.parse.parse_qs(self.path.split('?', 1)[1])
            
            if 'code' in params:
                captured_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>Success! You can close this window.</h1>")
                print(f"\n✅ Captured code: {captured_code[:30]}...")
            elif 'error' in params:
                print(f"\n❌ Error: {params['error'][0]}")
                print(f"   Description: {params.get('error_description', ['N/A'])[0]}")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n🌐 Waiting for callback on port {PORT}...")
        print("💡 If browser didn't open, paste this URL:")
        print(auth_url)
        print("\nPress Ctrl+C to cancel")
        httpd.timeout = 120  # 2 minutes
        
        while not captured_code:
            httpd.handle_request()
            if captured_code:
                break
        
        if not captured_code:
            print("\n❌ Timeout waiting for code")
            sys.exit(1)
            
except KeyboardInterrupt:
    print("\n\n❌ Cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Server error: {e}")
    sys.exit(1)

# Exchange code for token
print("\n📝 Step 2: Exchanging code for token...")

token_data = {
    'grant_type': 'authorization_code',
    'code': captured_code,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
}

req = urllib.request.Request(
    'https://www.linkedin.com/oauth/v2/accessToken',
    data=urllib.parse.urlencode(token_data).encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        access_token = result.get('access_token', '')
        expires_in = result.get('expires_in', 0)
        
        print(f"\n✅ Token received!")
        print(f"Access Token: {access_token}")
        print(f"Expires in: {expires_in}s")
        
        # Save to .env
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if 'Linkedin_Access_Token' in line or 'LINKEDIN_ACCESS_TOKEN' in line:
                new_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f'\nLINKEDIN_ACCESS_TOKEN={access_token}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"\n✅ Token saved to .env!")
        
        # Test token
        print("\n📝 Step 3: Testing token...")
        test_req = urllib.request.Request(
            'https://api.linkedin.com/v2/me',
            headers={'Authorization': f'Bearer {access_token}'},
            method='GET'
        )
        try:
            with urllib.request.urlopen(test_req, timeout=10) as resp:
                profile = json.loads(resp.read().decode())
                print(f"✅ Token valid! User: {profile.get('id', 'OK')}")
        except Exception as e:
            print(f"⚠️  Token test: {e}")
            
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"\n❌ Token exchange failed: {e.code}")
    print(f"Error: {error_body}")
except Exception as e:
    print(f"\n❌ Error: {e}")
