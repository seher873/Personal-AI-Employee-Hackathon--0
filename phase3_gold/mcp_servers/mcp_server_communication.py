#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Communication MCP Server
Gold Tier - Requirement #6

Port: 3002
Endpoints:
  POST /check-whatsapp - Check WhatsApp messages
  POST /check-gmail    - Check Gmail messages
  GET  /inbox          - Get inbox contents
  GET  /health         - Health check
"""

import os
import sys
import json
import io
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from skill_whatsapp import WhatsAppSkill
    from skill_gmail import GmailSkill
except ImportError:
    print("Warning: Could not import communication skills")
    WhatsAppSkill = None
    GmailSkill = None


PORT = 3002
PHASE3_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DIR = os.path.join(PHASE3_DIR, "Inbox")


class CommunicationMCPServer(BaseHTTPRequestHandler):
    """HTTP Request Handler for Communication MCP Server"""
    
    stats = {
        "requests": 0,
        "whatsapp_checks": 0,
        "gmail_checks": 0,
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
        CommunicationMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.handle_health()
        elif path == '/inbox':
            self.handle_get_inbox()
        elif path == '/stats':
            self.handle_stats()
        else:
            self.send_error_response("Not found", 404)
    
    def do_POST(self):
        CommunicationMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/check-whatsapp':
            self.handle_check_whatsapp()
        elif path == '/check-gmail':
            self.handle_check_gmail()
        else:
            self.send_error_response("Not found", 404)
    
    def handle_health(self):
        self.send_json_response({
            "status": "healthy",
            "service": "communication-mcp-server",
            "port": PORT,
            "stats": CommunicationMCPServer.stats
        })
    
    def handle_stats(self):
        self.send_json_response({
            "service": "communication-mcp-server",
            "stats": CommunicationMCPServer.stats
        })
    
    def handle_get_inbox(self):
        """Get inbox contents"""
        try:
            if not os.path.exists(INBOX_DIR):
                self.send_json_response({
                    "success": True,
                    "messages": [],
                    "count": 0
                })
                return
            
            messages = []
            for filename in sorted(os.listdir(INBOX_DIR), reverse=True)[:50]:  # Last 50
                if filename.endswith('.md'):
                    filepath = os.path.join(INBOX_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract metadata
                    messages.append({
                        "file": filename,
                        "preview": content[:200]
                    })
            
            self.send_json_response({
                "success": True,
                "messages": messages,
                "count": len(messages)
            })
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_check_whatsapp(self):
        """Check WhatsApp messages"""
        try:
            if WhatsAppSkill is None:
                self.send_error_response("WhatsAppSkill not available")
                return
            
            # Return info about WhatsApp monitoring
            self.send_json_response({
                "success": True,
                "message": "WhatsApp monitoring info",
                "info": {
                    "status": "Manual monitoring required",
                    "inbox_dir": INBOX_DIR,
                    "instruction": "Run skill_whatsapp.py to monitor messages"
                }
            })
            
            CommunicationMCPServer.stats["whatsapp_checks"] += 1
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_check_gmail(self):
        """Check Gmail messages"""
        try:
            if GmailSkill is None:
                self.send_error_response("GmailSkill not available")
                return
            
            gmail = GmailSkill()
            result = gmail.check_inbox(max_emails=10)
            
            CommunicationMCPServer.stats["gmail_checks"] += 1
            
            self.send_json_response({
                "success": True,
                "result": result,
                "emails_count": result.get("emails_count", 0)
            })
        except Exception as e:
            self.send_error_response(str(e))


def run_server():
    """Run the Communication MCP Server"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, CommunicationMCPServer)
    
    print(f"🚀 Communication MCP Server running on port {PORT}")
    print(f"   Endpoints:")
    print(f"   POST /check-whatsapp - Check WhatsApp")
    print(f"   POST /check-gmail    - Check Gmail")
    print(f"   GET  /inbox          - Get inbox contents")
    print(f"   GET  /health         - Health check")
    print(f"   GET  /stats          - Server statistics")
    print(f"\n   Started at: {CommunicationMCPServer.stats['start_time']}")
    
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n\nCommunication MCP Server stopped")
    except Exception as e:
        print(f"Server error: {e}")
