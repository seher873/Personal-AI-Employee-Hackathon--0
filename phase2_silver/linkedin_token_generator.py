#!/usr/bin/env python3
"""
LinkedIn Token Generator
========================
Generate new LinkedIn access token with proper scopes for posting

Scopes:
- w_member_social: Post to personal profile
- w_organization_social: Post to company pages
- r_organization_social: Read company info

Usage:
    py -3 linkedin_token_generator.py
"""

import os
import sys
import webbrowser
import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import threading
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip('"')
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip('"')

# LinkedIn OAuth URLs
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Required scopes for posting
SCOPES = [
    "w_member_social",           # Post to personal profile
    "r_liteprofile"              # Read basic profile
]

# Redirect URI (must match exactly with LinkedIn App settings)
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8081")
REDIRECT_PORT = int(REDIRECT_URI.split(":")[-1].split("/")[0]) if ":" in REDIRECT_URI else 8081


class AuthorizationHandler(http.server.BaseHTTPRequestHandler):
    """Handle OAuth redirect and capture authorization code"""
    
    authorization_code = None
    
    def do_GET(self):
        """Handle GET request from LinkedIn OAuth redirect"""
        if self.path.startswith('/callback'):
            # Parse authorization code from URL
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                self.authorization_code = params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>LinkedIn Authorization Successful</title>
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; }
                        .success { color: #28a745; }
                    </style>
                </head>
                <body>
                    <h1 class="success">✅ Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                return
            elif 'error' in params:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Error: {params['error'][0]}".encode())
                return
        
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


def get_authorization_url(redirect_uri: str = REDIRECT_URI) -> str:
    """Generate LinkedIn authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': LINKEDIN_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(SCOPES),
        'state': 'linkedin_token_generator_' + os.urandom(8).hex()
    }

    url = f"{LINKEDIN_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return url


def exchange_code_for_token(authorization_code: str) -> dict:
    """Exchange authorization code for access token"""
    print("\n🔄 Exchanging authorization code for access token...")
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    req = urllib.request.Request(
        LINKEDIN_TOKEN_URL,
        data=urllib.parse.urlencode(data).encode(),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ Token exchange failed: {e.code} - {error_body}")
        return {'error': e.code, 'error_description': error_body}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'error': str(e)}


def save_token_to_env(access_token: str):
    """Save new access token to .env file"""
    env_file = BASE_DIR / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read existing content
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and replace LINKEDIN_ACCESS_TOKEN line
    new_lines = []
    token_found = False
    
    for line in lines:
        if line.strip().startswith('LINKEDIN_ACCESS_TOKEN') or line.strip().startswith('Linkedin_Access_Token'):
            new_lines.append(f'LINKEDIN_ACCESS_TOKEN="{access_token}"\n')
            token_found = True
        else:
            new_lines.append(line)
    
    # If not found, append
    if not token_found:
        new_lines.append(f'\nLINKEDIN_ACCESS_TOKEN="{access_token}"\n')
    
    # Write back
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Token saved to .env file")
    return True


def test_token(access_token: str):
    """Test the new token"""
    print("\n🧪 Testing token...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Test 1: Get profile
    req = urllib.request.Request(
        'https://api.linkedin.com/v2/me',
        headers=headers,
        method='GET'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            profile = json.loads(response.read().decode())
            print(f"✅ Profile access: {profile.get('id', 'OK')}")
    except Exception as e:
        print(f"⚠️  Profile access: {e}")
    
    # Test 2: Get companies
    req = urllib.request.Request(
        'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organizationalTarget~(localizedName,vanityName)))',
        headers=headers,
        method='GET'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            companies = json.loads(response.read().decode())
            elements = companies.get('elements', [])
            if elements:
                print(f"✅ Company access: Found {len(elements)} company page(s)")
                for elem in elements:
                    company = elem.get('organizationalTarget~', {})
                    print(f"   - {company.get('localizedName', 'N/A')} ({company.get('vanityName', 'N/A')})")
            else:
                print("⚠️  No company pages found with admin access")
    except Exception as e:
        print(f"⚠️  Company access: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("🔑 LinkedIn Token Generator")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, default=None,
                       help='Authorization code (if you already have it)')
    parser.add_argument('--port', type=int, default=None,
                       help='Port for redirect URI (default: 8081)')
    args = parser.parse_args()
    
    # Check credentials
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        print("❌ Error: LinkedIn credentials not found in .env")
        print(f"   Client ID: {LINKEDIN_CLIENT_ID or 'MISSING'}")
        print(f"   Client Secret: {LINKEDIN_CLIENT_SECRET or 'MISSING'}")
        print("\n📝 Please add to .env:")
        print('   LINKEDIN_CLIENT_ID="your_client_id"')
        print('   LINKEDIN_CLIENT_SECRET="your_client_secret"')
        return 1
    
    print(f"✅ Client ID: {LINKEDIN_CLIENT_ID[:10]}...")
    print(f"✅ Client Secret: {LINKEDIN_CLIENT_SECRET[:10]}...")
    print(f"\n📋 Required Scopes:")
    for scope in SCOPES:
        print(f"   - {scope}")

    # Use provided code if available
    if args.code:
        authorization_code = args.code
        print(f"\n✅ Using provided authorization code")
    else:
        print("\n" + "=" * 60)
        print("📝 Step 1: Authorize Application")
        print("=" * 60)

        # Generate authorization URL
        port = args.port or REDIRECT_PORT
        redirect_uri = f"http://localhost:{port}"
        auth_url = get_authorization_url(redirect_uri)
        print(f"\n🔗 Opening authorization URL...")
        print(f"   (If browser doesn't open, copy this URL:)")
        print(f"   {auth_url}")

        # Open browser
        webbrowser.open(auth_url)

        # Start local server to capture callback
        port = args.port or REDIRECT_PORT
        redirect_uri = f"http://localhost:{port}"
        print(f"\n🌐 Waiting for authorization callback on {redirect_uri}...")

        handler = AuthorizationHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.timeout = 120  # 2 minute timeout

            # Run server in background thread
            def serve():
                while not handler.authorization_code:
                    httpd.handle_request()

            server_thread = threading.Thread(target=serve)
            server_thread.daemon = True
            server_thread.start()

            # Wait for authorization code
            start_time = threading.Event()
            start_time.wait(timeout=120)

            if not handler.authorization_code:
                print("\n❌ Authorization timeout - please try again")
                print("\n💡 Alternative: Copy the URL above, authorize manually,")
                print(f"   then run: py -3 {sys.argv[0]} --code YOUR_CODE")
                return 1

        print(f"\n✅ Authorization code received!")
        authorization_code = handler.authorization_code

    print("\n" + "=" * 60)
    print("📝 Step 2: Exchange Code for Token")
    print("=" * 60)

    # Exchange code for token
    token_result = exchange_code_for_token(authorization_code)
    
    if 'error' in token_result:
        print(f"\n❌ Failed to get access token")
        print(f"   Error: {token_result.get('error')}")
        print(f"   Details: {token_result.get('error_description', 'N/A')}")
        return 1
    
    access_token = token_result.get('access_token', '')
    expires_in = token_result.get('expires_in', 0)
    
    if not access_token:
        print(f"\n❌ No access token in response")
        print(f"   Response: {token_result}")
        return 1
    
    print(f"\n✅ Access Token Received!")
    print(f"   Token: {access_token[:30]}...")
    print(f"   Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
    
    print("\n" + "=" * 60)
    print("📝 Step 3: Save Token")
    print("=" * 60)
    
    # Save to .env
    if save_token_to_env(access_token):
        print("\n✅ Token saved successfully!")
        
        # Test the token
        print("\n" + "=" * 60)
        print("📝 Step 4: Test Token")
        print("=" * 60)
        test_token(access_token)
        
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print("\n✅ You can now use linkedin_api_poster.py:")
        print("   py -3 linkedin_api_poster.py --text \"Hello LinkedIn!\"")
        print("   py -3 linkedin_api_poster.py --company --text \"Company post\"")
    else:
        print("\n⚠️  Token not saved to .env - copy it manually:")
        print(f"   LINKEDIN_ACCESS_TOKEN=\"{access_token}\"")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
