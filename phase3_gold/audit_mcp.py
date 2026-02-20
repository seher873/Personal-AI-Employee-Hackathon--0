#!/usr/bin/env python3
"""
Audit MCP Server (Gold Tier)
============================
Python MCP server for audit and briefing generation

Endpoints:
- POST /generate_briefing - Generate CEO_Briefing.md from vault data
- GET  /health            - Health check
- GET  /vault-summary     - Summary of vault contents
- POST /audit             - Run audit and generate report

Reads from vault directories and generates CEO_Briefing.md
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

# Configuration
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "Logs"
INBOX_DIR = BASE_DIR / "Inbox"
PROCESSED_DIR = BASE_DIR / "Processed"
CEO_BRIEFING_FILE = BASE_DIR / "CEO_Briefing.md"
AUDIT_LOG_FILE = BASE_DIR / "Audit_Log.md"

# Vault content directories
VAULT_DIRS = {
    'linkedin': BASE_DIR / "LinkedIn",
    'whatsapp': BASE_DIR / "WhatsApp",
    'watchers': BASE_DIR / "Watchers",
    'skills': BASE_DIR / "Skills",
}

# Server configuration
SERVER_PORT = int(os.getenv("AUDIT_MCP_PORT", "3001"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'audit_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AuditMCP')


class VaultAnalyzer:
    """
    Agent Skill: Vault Content Analysis
    Analyzes vault directories and extracts insights
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def count_files(self, directory: Path, pattern: str = "*") -> int:
        """Count files in a directory"""
        if not directory.exists():
            return 0
        return len(list(directory.glob(pattern)))
    
    def get_recent_files(self, directory: Path, hours: int = 24) -> list:
        """Get files modified in the last N hours"""
        if not directory.exists():
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for f in directory.rglob("*"):
            if f.is_file():
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime > cutoff:
                        recent.append({
                            'path': str(f.relative_to(self.base_dir)),
                            'modified': mtime.isoformat(),
                            'size': f.stat().st_size
                        })
                except:
                    continue
        
        return sorted(recent, key=lambda x: x['modified'], reverse=True)
    
    def read_markdown_content(self, filepath: Path) -> str:
        """Read content from markdown file"""
        if not filepath.exists():
            return ""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def extract_key_metrics(self) -> dict:
        """Extract key metrics from vault"""
        metrics = {
            'total_files': 0,
            'inbox_items': 0,
            'processed_items': 0,
            'log_entries': 0,
            'platforms': {}
        }
        
        # Count inbox items
        if INBOX_DIR.exists():
            metrics['inbox_items'] = self.count_files(INBOX_DIR, "*.md")
        
        # Count processed items
        for platform_dir in VAULT_DIRS.values():
            if platform_dir.exists():
                processed = platform_dir / "Processed"
                if processed.exists():
                    metrics['processed_items'] += self.count_files(processed, "*.md")
        
        # Count log entries
        if LOGS_DIR.exists():
            metrics['log_entries'] = self.count_files(LOGS_DIR, "*.log")
        
        # Platform-specific metrics
        for platform, dir_path in VAULT_DIRS.items():
            if dir_path.exists():
                metrics['platforms'][platform] = {
                    'files': self.count_files(dir_path),
                    'recent': len(self.get_recent_files(dir_path, 24))
                }
        
        metrics['total_files'] = sum(p['files'] for p in metrics['platforms'].values())
        
        return metrics
    
    def analyze_inbox(self) -> dict:
        """
        Agent Skill: Inbox Content Analysis
        Analyze inbox messages and categorize
        """
        analysis = {
            'total': 0,
            'by_platform': {},
            'by_type': {},
            'recent_messages': []
        }
        
        if not INBOX_DIR.exists():
            return analysis
        
        for msg_file in INBOX_DIR.glob("*.md"):
            content = self.read_markdown_content(msg_file)
            analysis['total'] += 1
            
            # Extract platform
            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'whatsapp']:
                if platform.lower() in content.lower():
                    analysis['by_platform'][platform] = analysis['by_platform'].get(platform, 0) + 1
                    break
            
            # Extract type
            for msg_type in ['message', 'comment', 'mention', 'reply']:
                if msg_type.lower() in content.lower():
                    analysis['by_type'][msg_type] = analysis['by_type'].get(msg_type, 0) + 1
                    break
            
            # Get recent messages (last 5)
            if len(analysis['recent_messages']) < 5:
                try:
                    mtime = datetime.fromtimestamp(msg_file.stat().st_mtime)
                    analysis['recent_messages'].append({
                        'file': msg_file.name,
                        'modified': mtime.isoformat(),
                        'preview': content[:200] + "..." if len(content) > 200 else content
                    })
                except:
                    continue
        
        return analysis


class BriefingGenerator:
    """
    Agent Skill: CEO Briefing Generation
    Generates executive summaries from vault data
    """
    
    def __init__(self, analyzer: VaultAnalyzer):
        self.analyzer = analyzer
    
    def generate_briefing(self, period: str = "weekly") -> str:
        """
        Generate CEO briefing document
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            Generated briefing content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metrics = self.analyzer.extract_key_metrics()
        inbox_analysis = self.analyzer.analyze_inbox()
        
        # Determine period label
        period_labels = {
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly'
        }
        period_label = period_labels.get(period, 'Weekly')
        
        briefing = f"""# CEO Briefing - {period_label} Report

**Generated:** {timestamp}

---

## Executive Summary

This briefing summarizes the Gold Tier AI Employee Vault activities for the {period_label} period.

### Key Highlights
- **Total Inbox Items:** {metrics['inbox_items']}
- **Processed Items:** {metrics['processed_items']}
- **Active Platforms:** {len(metrics['platforms'])}
- **System Health:** {'✅ Healthy' if metrics['inbox_items'] > 0 else '⚠️ Review Needed'}

---

## Platform Activity

"""
        
        # Platform breakdown
        for platform, data in metrics['platforms'].items():
            briefing += f"### {platform.capitalize()}\n"
            briefing += f"- Files: {data['files']}\n"
            briefing += f"- Recent (24h): {data['recent']}\n\n"
        
        briefing += """---

## Inbox Analysis

"""
        
        # Inbox breakdown
        briefing += f"### Messages by Platform\n"
        if inbox_analysis['by_platform']:
            for platform, count in inbox_analysis['by_platform'].items():
                briefing += f"- **{platform.capitalize()}:** {count}\n"
        else:
            briefing += "- No messages categorized\n"
        
        briefing += f"\n### Messages by Type\n"
        if inbox_analysis['by_type']:
            for msg_type, count in inbox_analysis['by_type'].items():
                briefing += f"- **{msg_type.capitalize()}:** {count}\n"
        else:
            briefing += "- No messages categorized\n"
        
        briefing += """
---

## Recent Activity

"""
        
        # Recent messages
        if inbox_analysis['recent_messages']:
            for i, msg in enumerate(inbox_analysis['recent_messages'], 1):
                briefing += f"### {i}. {msg['file']}\n"
                briefing += f"**Modified:** {msg['modified']}\n\n"
                briefing += f"```\n{msg['preview']}\n```\n\n"
        else:
            briefing += "No recent inbox activity.\n\n"
        
        briefing += """---

## System Metrics

"""
        
        # System metrics
        briefing += f"- **Total Files:** {metrics['total_files']}\n"
        briefing += f"- **Log Files:** {metrics['log_entries']}\n"
        briefing += f"- **Inbox Items:** {metrics['inbox_items']}\n"
        briefing += f"- **Processed Items:** {metrics['processed_items']}\n"
        
        briefing += """
---

## Recommendations

"""
        
        # Generate recommendations based on data
        recommendations = []
        
        if metrics['inbox_items'] > 10:
            recommendations.append("📬 High inbox volume - consider processing pending messages")
        
        if metrics['processed_items'] == 0:
            recommendations.append("⚠️ No processed items - verify watcher scripts are running")
        
        for platform, data in metrics['platforms'].items():
            if data['recent'] == 0:
                recommendations.append(f"🔍 {platform.capitalize()} shows no recent activity - check credentials")
        
        if not recommendations:
            recommendations.append("✅ All systems operating normally")
        
        for rec in recommendations:
            briefing += f"- {rec}\n"
        
        briefing += f"""
---

## Next Steps

1. Review inbox messages requiring attention
2. Verify all platform credentials are current
3. Check audit logs for any errors
4. Schedule next briefing for {self._next_period(period)}

---

*Generated by Gold Tier Audit MCP Server*
"""
        
        return briefing
    
    def _next_period(self, period: str) -> str:
        """Calculate next briefing date"""
        now = datetime.now()
        
        if period == 'daily':
            next_date = now + timedelta(days=1)
        elif period == 'weekly':
            next_date = now + timedelta(weeks=1)
        else:
            next_date = now + timedelta(days=30)
        
        return next_date.strftime("%Y-%m-%d")
    
    def save_briefing(self, content: str) -> str:
        """Save briefing to file"""
        CEO_BRIEFING_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CEO_BRIEFING_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Briefing saved to {CEO_BRIEFING_FILE}")
        return str(CEO_BRIEFING_FILE)


class AuditMCPHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Audit MCP Server"""
    
    def __init__(self, *args, **kwargs):
        self.analyzer = VaultAnalyzer(BASE_DIR)
        self.briefing_gen = BriefingGenerator(self.analyzer)
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def send_json_response(self, data: dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_text_response(self, text: str, status: int = 200):
        """Send plain text response"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/health':
            self.handle_health()
        elif path == '/vault-summary':
            self.handle_vault_summary()
        elif path == '/briefing':
            self.handle_get_briefing()
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/generate_briefing':
            self.handle_generate_briefing()
        elif path == '/audit':
            self.handle_audit()
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def handle_health(self):
        """GET /health - Health check"""
        self.send_json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-gold',
            'service': 'Audit MCP Server'
        })
    
    def handle_vault_summary(self):
        """GET /vault-summary - Vault summary"""
        metrics = self.analyzer.extract_key_metrics()
        inbox = self.analyzer.analyze_inbox()
        
        self.send_json_response({
            'metrics': metrics,
            'inbox': inbox,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_get_briefing(self):
        """GET /briefing - Get current briefing"""
        if CEO_BRIEFING_FILE.exists():
            content = self.analyzer.read_markdown_content(CEO_BRIEFING_FILE)
            self.send_text_response(content)
        else:
            self.send_json_response({
                'error': 'No briefing found. Generate one first.',
                'hint': 'POST /generate_briefing'
            }, 404)
    
    def handle_generate_briefing(self):
        """POST /generate_briefing - Generate CEO briefing"""
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Parse request body
        period = 'weekly'  # default
        if content_length > 0:
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode())
                period = data.get('period', 'weekly')
            except:
                pass
        
        # Generate briefing
        try:
            briefing = self.briefing_gen.generate_briefing(period)
            filepath = self.briefing_gen.save_briefing(briefing)
            
            self.send_json_response({
                'success': True,
                'message': f'Briefing generated successfully',
                'file': filepath,
                'period': period,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Briefing generation error: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)
    
    def handle_audit(self):
        """POST /audit - Run audit"""
        try:
            # Generate audit log entry
            timestamp = datetime.now().isoformat()
            metrics = self.analyzer.extract_key_metrics()
            
            audit_entry = f"""### [{timestamp}] AUDIT

**System Audit Results:**
- Total Files: {metrics['total_files']}
- Inbox Items: {metrics['inbox_items']}
- Processed Items: {metrics['processed_items']}
- Log Files: {metrics['log_entries']}

**Status:** {'HEALTHY' if metrics['inbox_items'] > 0 else 'REVIEW_NEEDED'}

---

"""
            
            # Append to audit log
            AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            if not AUDIT_LOG_FILE.exists():
                with open(AUDIT_LOG_FILE, 'w') as f:
                    f.write("# Audit Log\n\n")
            
            with open(AUDIT_LOG_FILE, 'a') as f:
                f.write(audit_entry)
            
            self.send_json_response({
                'success': True,
                'message': 'Audit completed',
                'results': metrics,
                'timestamp': timestamp
            })
        except Exception as e:
            logger.error(f"Audit error: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)


def run_server(port: int = SERVER_PORT):
    """Run the Audit MCP Server"""
    # Ensure directories exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    
    server = HTTPServer(('0.0.0.0', port), AuditMCPHandler)
    
    print("=" * 60)
    print("📊 Audit MCP Server (Gold Tier)")
    print("=" * 60)
    print(f"📡 Server running on port {port}")
    print("")
    print("Endpoints:")
    print("  POST /generate_briefing - Generate CEO_Briefing.md")
    print("  GET  /briefing          - Get current briefing")
    print("  GET  /vault-summary     - Summary of vault contents")
    print("  POST /audit             - Run audit and generate report")
    print("  GET  /health            - Health check")
    print("")
    print("Example:")
    print("  curl -X POST http://localhost:" + str(port) + "/generate_briefing")
    print("  curl http://localhost:" + str(port) + "/vault-summary")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        server.shutdown()


if __name__ == '__main__':
    run_server()
