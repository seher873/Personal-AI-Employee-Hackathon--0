#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Server - Gold Tier
============================
Model Context Protocol (MCP) server for sending emails via Gmail

Port: 3003
Endpoints:
  POST /send-email    - Send email
  POST /send-briefing - Send CEO briefing via email
  GET  /health        - Health check
"""

import os
import sys
import json
import smtplib
import io
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

PORT = 3003
PHASE3_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Gmail configuration
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")  # App password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class EmailMCPServer(BaseHTTPRequestHandler):
    """HTTP Request Handler for Email MCP Server"""
    
    stats = {
        "requests": 0,
        "emails_sent": 0,
        "emails_failed": 0,
        "start_time": datetime.now().isoformat()
    }
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error_response(self, message, status=500):
        self.send_json_response({
            "success": False,
            "error": message
        }, status)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        EmailMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.handle_health()
        elif path == '/stats':
            self.handle_stats()
        else:
            self.send_error_response("Not found", 404)
    
    def do_POST(self):
        EmailMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/send-email':
            self.handle_send_email()
        elif path == '/send-briefing':
            self.handle_send_briefing()
        else:
            self.send_error_response("Not found", 404)
    
    def handle_health(self):
        """Health check endpoint"""
        self.send_json_response({
            "status": "healthy",
            "service": "email-mcp-server",
            "port": PORT,
            "credentials_set": bool(GMAIL_EMAIL and GMAIL_PASSWORD),
            "stats": EmailMCPServer.stats
        })
    
    def handle_stats(self):
        """Server statistics"""
        self.send_json_response({
            "service": "email-mcp-server",
            "stats": EmailMCPServer.stats
        })
    
    def handle_send_email(self):
        """Send email endpoint"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            to_email = data.get('to')
            subject = data.get('subject')
            body_text = data.get('body')
            cc = data.get('cc')
            html = data.get('html', False)
            
            if not to_email or not subject or not body_text:
                self.send_error_response("Missing required fields: to, subject, body", 400)
                return
            
            result = self.send_email(to_email, subject, body_text, cc, html)
            
            if result['success']:
                EmailMCPServer.stats["emails_sent"] += 1
            else:
                EmailMCPServer.stats["emails_failed"] += 1
            
            self.send_json_response(result)
            
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON", 400)
        except Exception as e:
            EmailMCPServer.stats["emails_failed"] += 1
            self.send_error_response(str(e))
    
    def handle_send_briefing(self):
        """Send CEO briefing via email"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            to_email = data.get('to')
            
            if not to_email:
                self.send_error_response("Missing 'to' email", 400)
                return
            
            # Read CEO briefing
            briefing_file = os.path.join(PHASE3_DIR, "CEO_Briefing.md")
            if not os.path.exists(briefing_file):
                self.send_error_response("CEO_Briefing.md not found", 404)
                return
            
            with open(briefing_file, 'r', encoding='utf-8') as f:
                briefing_content = f.read()
            
            result = self.send_email(
                to=to_email,
                subject=f"CEO Weekly Briefing - {datetime.now().strftime('%Y-%m-%d')}",
                body=briefing_content,
                html=False
            )
            
            if result['success']:
                EmailMCPServer.stats["emails_sent"] += 1
            
            self.send_json_response(result)
            
        except Exception as e:
            EmailMCPServer.stats["emails_failed"] += 1
            self.send_error_response(str(e))
    
    def send_email(self, to: str, subject: str, body: str, cc: str = None, html: bool = False) -> dict:
        """Send an email with optional CC"""
        
        if not GMAIL_EMAIL or not GMAIL_PASSWORD:
            return {
                'success': False,
                'message': 'Gmail credentials not configured. Set GMAIL_EMAIL and GMAIL_PASSWORD in .env'
            }
        
        try:
            msg = MIMEMultipart()
            msg['From'] = GMAIL_EMAIL
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            
            msg_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, msg_type))
            
            # Connect to SMTP server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            
            # Get all recipient addresses
            recipients = [to]
            if cc:
                recipients.extend(cc.split(','))
            
            server.sendmail(GMAIL_EMAIL, recipients, msg.as_string())
            server.quit()
            
            return {
                'success': True,
                'message': f'Email sent to {to}',
                'timestamp': datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'SMTP Authentication failed. Check Gmail App Password.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }


def run_server():
    """Run the Email MCP Server"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, EmailMCPServer)
    
    print(f"📧 Email MCP Server running on port {PORT}")
    print(f"   Endpoints:")
    print(f"   POST /send-email     - Send email")
    print(f"   POST /send-briefing  - Send CEO briefing")
    print(f"   GET  /health         - Health check")
    print(f"   GET  /stats          - Server statistics")
    print(f"\n   Gmail: {GMAIL_EMAIL if GMAIL_EMAIL else 'NOT CONFIGURED'}")
    print(f"   Started at: {EmailMCPServer.stats['start_time']}")
    
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n\nEmail MCP Server stopped")
    except Exception as e:
        print(f"Server error: {e}")
