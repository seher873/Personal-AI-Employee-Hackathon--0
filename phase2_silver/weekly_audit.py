#!/usr/bin/env python3
"""
Weekly Audit Script - Gold Tier
===============================
Automated weekly audit for AI Employee Vault

Agent Skill: Weekly Audit
- Runs every Sunday via cron
- Reads vault: Inbox/, Needs_Action/, Done/
- Generates CEO_Briefing.md with revenue, bottlenecks, tasks
- Uses Ralph Wiggum loop for robust analysis
- Calls audit_mcp.py endpoints
- Logs to Audit_Log.md

Cron Setup (run every Sunday at 9 AM):
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
# │ │ │ │ │
# 0 9 * * 0 cd /path/to/phase3_gold && source .venv/bin/activate && python weekly_audit.py >> Logs/weekly_audit.log 2>&1

Usage:
    python weekly_audit.py [--force] [--period weekly]
"""

import os
import sys
import json
import time
import random
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Configuration
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "Inbox"
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"
CEO_BRIEFING_FILE = BASE_DIR / "CEO_Briefing.md"
AUDIT_LOG_FILE = BASE_DIR / "Audit_Log.md"

# Audit MCP Server
AUDIT_MCP_URL = os.getenv("AUDIT_MCP_URL", "http://localhost:3001")

# Ralph Wiggum Loop Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_ANALYSIS_ITERATIONS = 5

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'weekly_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WeeklyAudit')


class RalphWiggumLoop:
    """
    Agent Skill: Ralph Wiggum Loop
    "Me fail English? That's unpossible!"
    
    Iterative analysis loop that keeps trying until successful.
    Used for robust data analysis and report generation.
    """
    
    def __init__(self, max_iterations: int = MAX_ANALYSIS_ITERATIONS):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.status = "pending"
    
    def start(self):
        """Start the loop"""
        self.current_iteration = 0
        self.status = "in_progress"
        logger.info("🍩 Ralph Wiggum Loop: 'I'm gonna analyze real hard!'")
    
    def next_iteration(self) -> bool:
        """Move to next iteration"""
        self.current_iteration += 1
        
        if self.current_iteration > self.max_iterations:
            logger.error(f"🍩 Ralph Wiggum Loop: Max iterations ({self.max_iterations}) reached")
            self.status = "failed"
            return False
        
        logger.info(f"🍩 Ralph Wiggum Loop: Iteration {self.current_iteration}/{self.max_iterations}")
        return True
    
    def complete(self):
        """Mark as complete"""
        self.status = "complete"
        logger.info("🍩 Ralph Wiggum Loop: TASK_COMPLETE - 'I did it!'")
    
    def fail(self):
        """Mark as failed"""
        self.status = "failed"
        logger.error("🍩 Ralph Wiggum Loop: TASK_FAILED - 'Me fail?'")
    
    def is_complete(self) -> bool:
        return self.status == "complete"
    
    def is_failed(self) -> bool:
        return self.status == "failed"


class VaultReader:
    """
    Agent Skill: Vault Content Reading
    Reads and categorizes content from vault directories
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def read_directory(self, dir_path: Path) -> List[Dict]:
        """Read all markdown files from a directory"""
        items = []
        
        if not dir_path.exists():
            logger.warning(f"Directory not found: {dir_path}")
            return items
        
        for md_file in dir_path.glob("*.md"):
            try:
                content = self.read_file(md_file)
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                
                items.append({
                    'file': md_file.name,
                    'path': str(md_file),
                    'content': content,
                    'modified': mtime.isoformat(),
                    'size': md_file.stat().st_size
                })
            except Exception as e:
                logger.error(f"Error reading {md_file}: {e}")
        
        return items
    
    def read_file(self, filepath: Path) -> str:
        """Read file content"""
        if not filepath.exists():
            return ""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def get_weekly_items(self, dir_path: Path) -> List[Dict]:
        """Get items modified in the last 7 days"""
        all_items = self.read_directory(dir_path)
        cutoff = datetime.now() - timedelta(days=7)
        
        weekly_items = []
        for item in all_items:
            try:
                modified = datetime.fromisoformat(item['modified'])
                if modified >= cutoff:
                    weekly_items.append(item)
            except:
                continue
        
        return weekly_items
    
    def categorize_items(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agent Skill: Content Categorization
        Categorize items by type (message, task, revenue, etc.)
        """
        categories = {
            'revenue': [],
            'bottlenecks': [],
            'tasks': [],
            'messages': [],
            'other': []
        }
        
        revenue_keywords = ['payment', 'revenue', 'sale', 'income', 'profit', '$', 'USD', 'PKR']
        bottleneck_keywords = ['blocked', 'stuck', 'waiting', 'issue', 'error', 'failed', 'problem', 'delay']
        task_keywords = ['task', 'todo', 'action', 'complete', 'done', 'pending', 'review']
        
        for item in items:
            content_lower = item['content'].lower()
            
            if any(kw in content_lower for kw in revenue_keywords):
                categories['revenue'].append(item)
            elif any(kw in content_lower for kw in bottleneck_keywords):
                categories['bottlenecks'].append(item)
            elif any(kw in content_lower for kw in task_keywords):
                categories['tasks'].append(item)
            else:
                categories['messages'].append(item)
        
        return categories


class AuditMCPClient:
    """
    Agent Skill: Audit MCP Integration
    Communicates with audit_mcp.py server
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def call_endpoint(self, endpoint: str, method: str = "GET", data: dict = None) -> Optional[dict]:
        """Call audit MCP endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                req = urllib.request.Request(url)
            else:  # POST
                body = json.dumps(data).encode('utf-8') if data else None
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        
        except urllib.error.URLError as e:
            logger.error(f"MCP call failed ({url}): {e}")
            return None
        except Exception as e:
            logger.error(f"MCP call error ({url}): {e}")
            return None
    
    def generate_briefing(self, period: str = "weekly") -> Optional[dict]:
        """Call audit_mcp to generate briefing"""
        logger.info("Calling audit_mcp /generate_briefing...")
        
        result = self.call_endpoint(
            "/generate_briefing",
            method="POST",
            data={'period': period}
        )
        
        if result and result.get('success'):
            logger.info(f"Briefing generated: {result.get('file')}")
        else:
            logger.warning("Briefing generation may have failed")
        
        return result
    
    def get_vault_summary(self) -> Optional[dict]:
        """Get vault summary from audit_mcp"""
        logger.info("Calling audit_mcp /vault-summary...")
        return self.call_endpoint("/vault-summary")
    
    def run_audit(self) -> Optional[dict]:
        """Trigger audit via audit_mcp"""
        logger.info("Calling audit_mcp /audit...")
        return self.call_endpoint("/audit", method="POST")
    
    def check_health(self) -> bool:
        """Check if audit_mcp is running"""
        result = self.call_endpoint("/health")
        return result is not None and result.get('status') == 'healthy'


class WeeklyAuditor:
    """
    Agent Skill: Weekly Audit
    Main audit orchestrator combining all components
    """
    
    def __init__(self):
        self.vault_reader = VaultReader(BASE_DIR)
        self.mcp_client = AuditMCPClient(AUDIT_MCP_URL)
        self.ralph_loop = RalphWiggumLoop()
        self.audit_data = {
            'period_start': (datetime.now() - timedelta(days=7)).isoformat(),
            'period_end': datetime.now().isoformat(),
            'inbox': [],
            'needs_action': [],
            'done': [],
            'revenue': [],
            'bottlenecks': [],
            'tasks': [],
            'summary': {}
        }
    
    def read_vault(self):
        """Read vault directories"""
        logger.info("📂 Reading vault directories...")
        
        self.audit_data['inbox'] = self.vault_reader.get_weekly_items(INBOX_DIR)
        self.audit_data['needs_action'] = self.vault_reader.get_weekly_items(NEEDS_ACTION_DIR)
        self.audit_data['done'] = self.vault_reader.get_weekly_items(DONE_DIR)
        
        logger.info(f"  Inbox: {len(self.audit_data['inbox'])} items")
        logger.info(f"  Needs Action: {len(self.audit_data['needs_action'])} items")
        logger.info(f"  Done: {len(self.audit_data['done'])} items")
    
    def analyze_with_ralph_loop(self):
        """
        Analyze vault data using Ralph Wiggum Loop
        Agent Skill: Iterative robust analysis
        """
        logger.info("🍩 Starting Ralph Wiggum analysis loop...")
        
        self.ralph_loop.start()
        
        while self.ralph_loop.next_iteration():
            try:
                # Combine all items for analysis
                all_items = (
                    self.audit_data['inbox'] +
                    self.audit_data['needs_action'] +
                    self.audit_data['done']
                )
                
                if not all_items:
                    logger.info("No items to analyze")
                    break
                
                # Categorize items
                categorized = self.vault_reader.categorize_items(all_items)
                
                self.audit_data['revenue'] = categorized['revenue']
                self.audit_data['bottlenecks'] = categorized['bottlenecks']
                self.audit_data['tasks'] = categorized['tasks']
                
                # Analysis successful
                self.ralph_loop.complete()
                logger.info(f"  Revenue items: {len(categorized['revenue'])}")
                logger.info(f"  Bottlenecks: {len(categorized['bottlenecks'])}")
                logger.info(f"  Tasks: {len(categorized['tasks'])}")
                break
                
            except Exception as e:
                logger.error(f"Analysis iteration failed: {e}")
                
                if not self.ralph_loop.next_iteration():
                    self.ralph_loop.fail()
                    logger.error("Ralph Wiggum Loop exhausted - using partial data")
    
    def generate_ceo_briefing(self) -> str:
        """
        Generate CEO_Briefing.md content
        Agent Skill: Executive Summary Generation
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        week_start = datetime.now() - timedelta(days=7)
        
        # Calculate metrics
        total_items = (
            len(self.audit_data['inbox']) +
            len(self.audit_data['needs_action']) +
            len(self.audit_data['done'])
        )
        
        completed_tasks = len(self.audit_data['done'])
        pending_tasks = len(self.audit_data['needs_action'])
        bottlenecks_count = len(self.audit_data['bottlenecks'])
        
        # Revenue summary
        revenue_text = ""
        if self.audit_data['revenue']:
            revenue_text = f"**Identified Revenue Items:** {len(self.audit_data['revenue'])}\n\n"
            for item in self.audit_data['revenue'][:5]:
                revenue_text += f"- {item['file']}\n"
        else:
            revenue_text = "*No revenue items identified this week.*\n"
        
        # Bottlenecks
        bottlenecks_text = ""
        if self.audit_data['bottlenecks']:
            bottlenecks_text = f"**Critical Issues:** {len(self.audit_data['bottlenecks'])}\n\n"
            for item in self.audit_data['bottlenecks'][:5]:
                bottlenecks_text += f"- ⚠️ {item['file']}\n"
        else:
            bottlenecks_text = "*No critical bottlenecks identified.*\n"
        
        # Tasks
        tasks_text = ""
        if self.audit_data['tasks']:
            tasks_text = f"**Tasks Processed:** {completed_tasks} completed, {pending_tasks} pending\n\n"
        else:
            tasks_text = "*No tasks identified.*\n"
        
        briefing = f"""# CEO Weekly Briefing

**Generated:** {timestamp}
**Period:** {week_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}

---

## Executive Summary

This weekly audit summarizes the Gold Tier AI Employee Vault activities.

### Key Metrics
- **Total Items Processed:** {total_items}
- **Tasks Completed:** {completed_tasks}
- **Tasks Pending:** {pending_tasks}
- **Bottlenecks Identified:** {bottlenecks_count}

---

## Revenue

{revenue_text}
---

## Bottlenecks

{bottlenecks_text}
---

## Tasks

{tasks_text}
---

## Inbox Summary

- **New Messages:** {len(self.audit_data['inbox'])}
- **Needs Action:** {len(self.audit_data['needs_action'])}
- **Completed:** {len(self.audit_data['done'])}

---

## Recommendations

"""
        
        # Generate recommendations
        recommendations = []
        
        if bottlenecks_count > 0:
            recommendations.append(f"🔴 **Priority:** Address {bottlenecks_count} bottleneck(s) immediately")
        
        if pending_tasks > 5:
            recommendations.append(f"📋 **Action:** {pending_tasks} tasks pending review")
        
        if len(self.audit_data['inbox']) > 10:
            recommendations.append("📬 **Inbox:** High volume - process pending messages")
        
        if completed_tasks > 0:
            recommendations.append(f"✅ **Progress:** {completed_tasks} tasks completed this week")
        
        if not recommendations:
            recommendations.append("✅ All systems operating normally")
        
        for rec in recommendations:
            briefing += f"{rec}\n"
        
        briefing += f"""
---

## Next Audit

**Scheduled:** Next Sunday at 9:00 AM

---

*Generated by Gold Tier Weekly Audit System*
*Agent Skill: Weekly Audit*
"""
        
        return briefing
    
    def save_briefing(self, content: str) -> str:
        """Save briefing to file"""
        CEO_BRIEFING_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CEO_BRIEFING_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"💾 Briefing saved to {CEO_BRIEFING_FILE}")
        return str(CEO_BRIEFING_FILE)
    
    def log_audit(self, content: str):
        """Log audit to Audit_Log.md"""
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"""### [{timestamp}] WEEKLY_AUDIT

{content}

---

"""
        
        if not AUDIT_LOG_FILE.exists():
            with open(AUDIT_LOG_FILE, 'w') as f:
                f.write("# Audit Log\n\n## Gold Tier Weekly Audits\n\n")
        
        with open(AUDIT_LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        logger.info(f"📝 Audit logged to {AUDIT_LOG_FILE}")
    
    def run(self) -> bool:
        """
        Run complete weekly audit
        Agent Skill: Weekly Audit Orchestration
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Weekly Audit")
        logger.info("=" * 60)
        
        success = True
        
        # Step 1: Check audit_mcp health
        logger.info("\n📊 Step 1: Checking audit_mcp health...")
        if self.mcp_client.check_health():
            logger.info("✅ audit_mcp is healthy")
        else:
            logger.warning("⚠️ audit_mcp not responding - will run standalone")
        
        # Step 2: Read vault
        logger.info("\n📂 Step 2: Reading vault...")
        self.read_vault()
        
        # Step 3: Analyze with Ralph Wiggum loop
        logger.info("\n🍩 Step 3: Analyzing data...")
        self.analyze_with_ralph_loop()
        
        # Step 4: Generate briefing
        logger.info("\n📄 Step 4: Generating CEO briefing...")
        briefing = self.generate_ceo_briefing()
        briefing_path = self.save_briefing(briefing)
        
        # Step 5: Call audit_mcp to also generate briefing
        logger.info("\n📡 Step 5: Calling audit_mcp...")
        mcp_result = self.mcp_client.generate_briefing("weekly")
        if mcp_result and mcp_result.get('success'):
            logger.info(f"✅ audit_mcp briefing: {mcp_result.get('file')}")
        else:
            logger.info("Using locally generated briefing")
        
        # Step 6: Log audit
        logger.info("\n📝 Step 6: Logging audit...")
        log_content = f"""**Weekly Audit Completed**
- Period: {self.audit_data['period_start']} to {self.audit_data['period_end']}
- Total Items: {len(self.audit_data['inbox']) + len(self.audit_data['needs_action']) + len(self.audit_data['done'])}
- Revenue Items: {len(self.audit_data['revenue'])}
- Bottlenecks: {len(self.audit_data['bottlenecks'])}
- Tasks: {len(self.audit_data['tasks'])}
- Briefing: {briefing_path}"""
        
        self.log_audit(log_content)
        
        # Step 7: Trigger audit_mcp audit
        logger.info("\n🔍 Step 7: Running audit_mcp audit...")
        audit_result = self.mcp_client.run_audit()
        if audit_result and audit_result.get('success'):
            logger.info("✅ audit_mcp audit completed")
        else:
            logger.info("Audit logged locally")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Weekly Audit Complete")
        logger.info("=" * 60)
        logger.info(f"📄 Briefing: {briefing_path}")
        logger.info(f"📝 Audit Log: {AUDIT_LOG_FILE}")
        
        return success


def main():
    """Main entry point"""
    print("=" * 60)
    print("📊 Gold Tier Weekly Audit")
    print("=" * 60)
    print()
    print("Agent Skill: Weekly Audit")
    print("🍩 Ralph Wiggum Loop enabled")
    print("📡 audit_mcp integration enabled")
    print()
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Weekly Audit Script')
    parser.add_argument('--force', action='store_true',
                       help='Force run even if not Sunday')
    parser.add_argument('--period', type=str, default='weekly',
                       choices=['daily', 'weekly', 'monthly'],
                       help='Audit period')
    args = parser.parse_args()
    
    # Check if Sunday (unless --force)
    today = datetime.now()
    if today.weekday() != 6 and not args.force:
        print(f"⚠️  Today is {today.strftime('%A')}, not Sunday.")
        print("   Use --force to run anyway.")
        print()
        print("Cron schedule (Sundays at 9 AM):")
        print("   0 9 * * 0 cd /path/to/phase3_gold && python weekly_audit.py")
        return 1
    
    print(f"📅 Audit Date: {today.strftime('%Y-%m-%d')}")
    print(f"📊 Period: {args.period}")
    print()
    
    # Ensure directories exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run audit
    auditor = WeeklyAuditor()
    success = auditor.run()
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Briefing: {CEO_BRIEFING_FILE}")
    print(f"  Audit Log: {AUDIT_LOG_FILE}")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
