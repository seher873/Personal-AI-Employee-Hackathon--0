#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit MCP Server
Gold Tier - Requirement #6

Port: 3001
Endpoints:
  POST /generate_briefing - Generate CEO_Briefing.md
  GET  /briefing          - Get current briefing
  GET  /vault-summary     - Summary of vault contents
  POST /audit             - Run full audit
  GET  /health            - Health check
"""

import os
import sys
import json
import io
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from skill_weekly_audit import WeeklyAuditSkill
except ImportError:
    print("Warning: Could not import WeeklyAuditSkill")
    WeeklyAuditSkill = None


PORT = 3001
PHASE3_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AuditMCPServer(BaseHTTPRequestHandler):
    """HTTP Request Handler for Audit MCP Server"""
    
    # Store server stats
    stats = {
        "requests": 0,
        "briefings_generated": 0,
        "audits_run": 0,
        "start_time": datetime.now().isoformat()
    }
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error_response(self, message, status=500):
        """Send error response"""
        self.send_json_response({
            "success": False,
            "error": message
        }, status)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        AuditMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.handle_health()
        elif path == '/briefing':
            self.handle_get_briefing()
        elif path == '/vault-summary':
            self.handle_vault_summary()
        elif path == '/stats':
            self.handle_stats()
        else:
            self.send_error_response("Not found", 404)
    
    def do_POST(self):
        """Handle POST requests"""
        AuditMCPServer.stats["requests"] += 1
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/generate_briefing':
            self.handle_generate_briefing()
        elif path == '/audit':
            self.handle_audit()
        else:
            self.send_error_response("Not found", 404)
    
    def handle_health(self):
        """Health check endpoint"""
        self.send_json_response({
            "status": "healthy",
            "service": "audit-mcp-server",
            "port": PORT,
            "uptime": datetime.now().isoformat(),
            "stats": AuditMCPServer.stats
        })
    
    def handle_stats(self):
        """Server statistics"""
        self.send_json_response({
            "service": "audit-mcp-server",
            "stats": AuditMCPServer.stats
        })
    
    def handle_get_briefing(self):
        """Get current CEO briefing"""
        try:
            # Look for latest briefing
            reports_dir = os.path.join(PHASE3_DIR, "Reports")
            briefing_file = os.path.join(PHASE3_DIR, "CEO_Briefing.md")
            
            if os.path.exists(briefing_file):
                with open(briefing_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_json_response({
                    "success": True,
                    "briefing": content,
                    "path": briefing_file
                })
            else:
                self.send_error_response("No briefing found. Run /generate_briefing first", 404)
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_generate_briefing(self):
        """Generate CEO briefing"""
        try:
            if WeeklyAuditSkill is None:
                self.send_error_response("WeeklyAuditSkill not available")
                return
            
            audit = WeeklyAuditSkill()
            briefing_path = audit.generate_ceo_briefing()
            
            AuditMCPServer.stats["briefings_generated"] += 1
            
            self.send_json_response({
                "success": True,
                "message": "CEO briefing generated",
                "path": briefing_path
            })
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_vault_summary(self):
        """Get summary of vault contents"""
        try:
            summary = {
                "directories": {},
                "files": {},
                "logs": {}
            }
            
            # Count directories
            for item in os.listdir(PHASE3_DIR):
                item_path = os.path.join(PHASE3_DIR, item)
                if os.path.isdir(item_path):
                    if item not in ['node_modules', '.venv', '__pycache__']:
                        count = sum(len(files) for _, _, files in os.walk(item_path))
                        summary["directories"][item] = count
            
            # Count log files
            logs_dir = os.path.join(PHASE3_DIR, "Logs")
            if os.path.exists(logs_dir):
                log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
                summary["logs"] = {
                    "count": len(log_files),
                    "files": log_files
                }
            
            # Count inbox items
            inbox_dir = os.path.join(PHASE3_DIR, "Inbox")
            if os.path.exists(inbox_dir):
                inbox_count = len([f for f in os.listdir(inbox_dir) if f.endswith('.md')])
                summary["files"]["inbox_items"] = inbox_count
            
            # Count reports
            reports_dir = os.path.join(PHASE3_DIR, "Reports")
            if os.path.exists(reports_dir):
                report_count = len([f for f in os.listdir(reports_dir) if f.endswith('.json') or f.endswith('.md')])
                summary["files"]["reports"] = report_count
            
            self.send_json_response({
                "success": True,
                "summary": summary
            })
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_audit(self):
        """Run full audit"""
        try:
            if WeeklyAuditSkill is None:
                self.send_error_response("WeeklyAuditSkill not available")
                return
            
            audit = WeeklyAuditSkill()
            report = audit.generate_weekly_report()
            
            AuditMCPServer.stats["audits_run"] += 1
            
            self.send_json_response({
                "success": True,
                "message": "Audit completed",
                "report": report
            })
        except Exception as e:
            self.send_error_response(str(e))


def run_server():
    """Run the Audit MCP Server"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AuditMCPServer)
    
    print(f"🚀 Audit MCP Server running on port {PORT}")
    print(f"   Endpoints:")
    print(f"   POST /generate_briefing - Generate CEO briefing")
    print(f"   GET  /briefing          - Get current briefing")
    print(f"   GET  /vault-summary     - Vault summary")
    print(f"   POST /audit             - Run full audit")
    print(f"   GET  /health            - Health check")
    print(f"   GET  /stats             - Server statistics")
    print(f"\n   Started at: {AuditMCPServer.stats['start_time']}")
    
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n\nAudit MCP Server stopped")
    except Exception as e:
        print(f"Server error: {e}")
