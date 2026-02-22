#!/usr/bin/env python3
"""
Setup Cron Jobs for AI Employee Vault
======================================
Silver + Gold Tier Scheduling

Agent Skills:
- Scheduling Skill (Cron)
- Automated watcher/poster/audit execution

This script sets up cron jobs for:
- Watchers: Every minute (Gmail, WhatsApp, LinkedIn, FB/IG, Twitter)
- Posters: Daily at 9 AM (LinkedIn, FB/IG, Twitter)
- Weekly Audit: Sundays at 8 AM
- Orchestrator: Every 5 minutes

Usage:
    python setup_cron.py [--install|--remove|--list|--dry-run]
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
PYTHON_PATH = sys.executable
LOGS_DIR = BASE_DIR / "Logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CRON_LOG = LOGS_DIR / "cron.log"

# Cron job definitions
CRON_JOBS = {
    # Watchers - Every minute
    "gmail_watcher": {
        "schedule": "* * * * *",
        "script": "gmail_watcher.py",
        "description": "Gmail Watcher - Check for new emails every minute"
    },
    "whatsapp_watcher": {
        "schedule": "* * * * *",
        "script": "whatsapp_watcher.py",
        "description": "WhatsApp Watcher - Check for new messages every minute"
    },
    "linkedin_watcher": {
        "schedule": "* * * * *",
        "script": "linkedin_watcher.py",
        "description": "LinkedIn Watcher - Check for interactions every minute"
    },
    "fb_ig_watcher": {
        "schedule": "* * * * *",
        "script": "fb_ig_browser_watcher.py",
        "description": "Facebook/Instagram Watcher - Check for interactions every minute"
    },
    "twitter_watcher": {
        "schedule": "* * * * *",
        "script": "twitter_browser_watcher.py",
        "description": "Twitter/X Watcher - Check for interactions every minute"
    },
    
    # Posters - Daily at 9 AM
    "linkedin_poster": {
        "schedule": "0 9 * * *",
        "script": "linkedin_browser_poster.py",
        "description": "LinkedIn Poster - Daily post at 9 AM"
    },
    "fb_ig_poster": {
        "schedule": "0 9 * * *",
        "script": "fb_ig_browser_poster.py",
        "description": "Facebook/Instagram Poster - Daily post at 9 AM"
    },
    "twitter_poster": {
        "schedule": "0 9 * * *",
        "script": "twitter_browser_poster.py",
        "description": "Twitter/X Poster - Daily post at 9 AM"
    },
    
    # Orchestrator - Every 5 minutes
    "orchestrator": {
        "schedule": "*/5 * * * *",
        "script": "ai_orchestrator.py",
        "description": "AI Orchestrator - Process inbox every 5 minutes"
    },
    
    # Weekly Audit - Sundays at 8 AM
    "weekly_audit": {
        "schedule": "0 8 * * 0",
        "script": "weekly_audit.py",
        "description": "Weekly Audit - CEO briefing every Sunday at 8 AM"
    }
}


def get_crontab_entry(job_name: str, job_config: dict) -> str:
    """Generate a crontab entry for a job"""
    script_path = BASE_DIR / job_config["script"]
    
    # Change to script directory before running
    cmd = f"cd {BASE_DIR} && {PYTHON_PATH} {script_path} >> {CRON_LOG} 2>&1"
    
    return f"# {job_config['description']}\n{job_config['schedule']} {cmd}\n"


def get_current_crontab() -> str:
    """Get current crontab content"""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def install_crontab(content: str) -> bool:
    """Install new crontab content"""
    try:
        # Write to temp file first
        temp_file = "/tmp/crontab_temp.txt"
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Install crontab
        result = subprocess.run(
            ["crontab", temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up temp file
        os.remove(temp_file)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error installing crontab: {result.stderr}")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error: {e}")
        return False


def generate_crontab(existing: str = "", enabled_jobs: list = None) -> str:
    """Generate complete crontab content"""
    header = f"""# AI Employee Vault - Cron Jobs
# Generated: {datetime.now().isoformat()}
# Base Directory: {BASE_DIR}
# Python: {PYTHON_PATH}
# Log File: {CRON_LOG}
#
# To view logs: tail -f {CRON_LOG}
# To edit: crontab -e
# To remove: python setup_cron.py --remove
#
# ============================================

"""
    
    # Keep existing non-AI jobs
    existing_lines = []
    if existing:
        in_ai_section = False
        for line in existing.split('\n'):
            if 'AI Employee Vault' in line:
                in_ai_section = True
                continue
            if not in_ai_section and line.strip() and not line.startswith('# AI Employee'):
                existing_lines.append(line)
    
    existing_content = '\n'.join(existing_lines)
    if existing_content.strip():
        existing_content += "\n\n"
    
    # Build new crontab
    crontab = header + existing_content
    
    # Add AI Employee jobs
    if enabled_jobs is None:
        enabled_jobs = list(CRON_JOBS.keys())
    
    for job_name, job_config in CRON_JOBS.items():
        if job_name in enabled_jobs:
            crontab += get_crontab_entry(job_name, job_config) + "\n"
    
    return crontab


def print_crontab_preview(content: str):
    """Print a preview of the crontab"""
    print("\n" + "=" * 70)
    print("📋 CRONTAB PREVIEW")
    print("=" * 70)
    
    lines = content.split('\n')
    for i, line in enumerate(lines[:30]):  # Show first 30 lines
        print(line)
    
    if len(lines) > 30:
        print(f"... and {len(lines) - 30} more lines")
    
    print("=" * 70 + "\n")


def check_cron_service() -> bool:
    """Check if cron service is running"""
    try:
        # Try different methods to check cron
        for cmd in [["systemctl", "is-active", "cron"], 
                    ["systemctl", "is-active", "crond"],
                    ["service", "cron", "status"]]:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
            except:
                continue
        
        # If systemctl fails, try pgrep
        result = subprocess.run(
            ["pgrep", "-x", "cron"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
        
    except Exception as e:
        print(f"Warning: Could not check cron service: {e}")
        return True  # Assume OK on WSL


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup cron jobs for AI Employee Vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_cron.py --install      # Install all cron jobs
  python setup_cron.py --remove       # Remove AI Employee cron jobs
  python setup_cron.py --list         # Show current crontab
  python setup_cron.py --dry-run      # Preview without installing
  python setup_cron.py --watchers     # Install only watchers
  python setup_cron.py --posters      # Install only posters
        """
    )
    
    parser.add_argument('--install', action='store_true',
                       help='Install all cron jobs')
    parser.add_argument('--remove', action='store_true',
                       help='Remove AI Employee cron jobs')
    parser.add_argument('--list', action='store_true',
                       help='List current crontab')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview crontab without installing')
    parser.add_argument('--watchers', action='store_true',
                       help='Install only watcher jobs')
    parser.add_argument('--posters', action='store_true',
                       help='Install only poster jobs')
    parser.add_argument('--audit', action='store_true',
                       help='Install only weekly audit')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🤖 AI Employee Vault - Cron Job Setup")
    print("=" * 70)
    print(f"\n📁 Base Directory: {BASE_DIR}")
    print(f"🐍 Python: {PYTHON_PATH}")
    print(f"📝 Log File: {CRON_LOG}")
    print()
    
    # Check if running on supported system
    if platform.system() == 'Windows':
        print("❌ Windows detected. Cron is not available on Windows.")
        print("   Use Task Scheduler instead:")
        print("   1. Open Task Scheduler")
        print("   2. Create Basic Task")
        print("   3. Set trigger (daily/hourly/etc)")
        print("   4. Action: Start a program")
        print(f"   5. Program: {PYTHON_PATH}")
        print(f"   6. Arguments: {BASE_DIR}\\script.py")
        sys.exit(1)
    
    # Check cron service
    if not check_cron_service():
        print("⚠️  Cron service may not be running.")
        print("   Try: sudo service cron start")
        print()
    
    # Handle arguments
    if args.list:
        current = get_current_crontab()
        if current:
            print("\n📋 Current Crontab:")
            print("-" * 70)
            print(current)
            print("-" * 70)
        else:
            print("\n📋 No crontab installed")
        sys.exit(0)
    
    if args.remove:
        print("\n🗑️  Removing AI Employee cron jobs...")
        current = get_current_crontab()
        
        # Remove AI Employee section
        lines = current.split('\n')
        filtered_lines = []
        in_ai_section = False
        
        for line in lines:
            if 'AI Employee Vault' in line:
                in_ai_section = True
                continue
            if in_ai_section and line.startswith('#'):
                continue
            if in_ai_section and line.strip() == '':
                continue
            if in_ai_section and not line.startswith('# AI Employee'):
                # Check if it's an AI job line
                if str(BASE_DIR) in line:
                    continue
                in_ai_section = False
                filtered_lines.append(line)
            else:
                filtered_lines.append(line)
        
        new_crontab = '\n'.join(filtered_lines)
        
        if install_crontab(new_crontab):
            print("✅ AI Employee cron jobs removed")
        else:
            print("❌ Failed to remove cron jobs")
        sys.exit(0)
    
    # Determine which jobs to install
    enabled_jobs = None  # All jobs by default
    
    if args.watchers:
        enabled_jobs = [k for k in CRON_JOBS.keys() if 'watcher' in k]
    elif args.posters:
        enabled_jobs = [k for k in CRON_JOBS.keys() if 'poster' in k]
    elif args.audit:
        enabled_jobs = ['weekly_audit']
    
    # Generate crontab
    current = get_current_crontab()
    new_crontab = generate_crontab(current, enabled_jobs)
    
    if args.dry_run or not args.install:
        print("\n📋 Jobs to install:")
        print("-" * 70)
        
        jobs_to_show = enabled_jobs if enabled_jobs else list(CRON_JOBS.keys())
        for job_name in jobs_to_show:
            if job_name in CRON_JOBS:
                config = CRON_JOBS[job_name]
                print(f"  {config['schedule']}  {config['script']}")
                print(f"    → {config['description']}")
                print()
        
        print("-" * 70)
        print_crontab_preview(new_crontab)
        
        if not args.install:
            print("\n💡 Run with --install to install these cron jobs")
            print("   Or use --dry-run to preview only")
            sys.exit(0)
    
    # Install
    if args.install:
        print("\n📦 Installing cron jobs...")
        
        if install_crontab(new_crontab):
            print("✅ Cron jobs installed successfully!")
            print("\n📋 Installed jobs:")
            
            jobs_installed = enabled_jobs if enabled_jobs else list(CRON_JOBS.keys())
            for job_name in jobs_installed:
                if job_name in CRON_JOBS:
                    config = CRON_JOBS[job_name]
                    print(f"  ✅ {config['description']}")
            
            print(f"\n📝 Logs will be written to: {CRON_LOG}")
            print("\n🔍 To view logs: tail -f " + str(CRON_LOG))
            print("🔍 To view crontab: crontab -l")
            print("🔍 To remove: python setup_cron.py --remove")
        else:
            print("❌ Failed to install cron jobs")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ Setup complete!")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
