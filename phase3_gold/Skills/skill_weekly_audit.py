"""
Agent Skill: Weekly Audit & CEO Briefing
Gold Tier - Requirement #7

Generates weekly business audit report and CEO briefing.

Usage:
    from skill_weekly_audit import WeeklyAuditSkill
    audit = WeeklyAuditSkill()
    audit.generate_weekly_report()
    briefing = audit.generate_ceo_briefing()
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class WeeklyAuditSkill:
    """Weekly audit and CEO briefing generation skill."""
    
    def __init__(self):
        self.log_dir = "./Logs"
        self.inbox_dir = "./Inbox"
        self.done_dir = "./Done"
        self.report_dir = "./Reports"
        
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.done_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        self._log("WeeklyAuditSkill initialized")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = os.path.join(self.log_dir, f"audit_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _get_week_range(self):
        """Get current week's date range."""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_of_week, end_of_week
    
    def _count_files_in_dir(self, directory, prefix=None):
        """Count files in a directory."""
        if not os.path.exists(directory):
            return 0
        
        count = 0
        for f in os.listdir(directory):
            if prefix and not f.startswith(prefix):
                continue
            count += 1
        return count
    
    def _parse_log_file(self, filepath):
        """Parse a log file and extract statistics."""
        stats = {
            "total_lines": 0,
            "errors": 0,
            "warnings": 0,
            "success": 0
        }
        
        if not os.path.exists(filepath):
            return stats
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    stats["total_lines"] += 1
                    if "ERROR" in line or "error" in line.lower():
                        stats["errors"] += 1
                    elif "WARN" in line or "warning" in line.lower():
                        stats["warnings"] += 1
                    elif "success" in line.lower() or "successful" in line.lower():
                        stats["success"] += 1
        except:
            pass
        
        return stats
    
    def _collect_platform_stats(self, platform):
        """Collect statistics for a platform."""
        log_prefix = platform.lower()
        log_file = os.path.join(self.log_dir, f"{log_prefix}_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Get all log files for this platform
        platform_logs = []
        if os.path.exists(self.log_dir):
            for f in os.listdir(self.log_dir):
                if f.startswith(log_prefix) and f.endswith('.log'):
                    platform_logs.append(os.path.join(self.log_dir, f))
        
        # Aggregate stats
        total_stats = {
            "total_lines": 0,
            "errors": 0,
            "warnings": 0,
            "success": 0,
            "posts": 0,
            "messages": 0
        }
        
        for log_file in platform_logs:
            stats = self._parse_log_file(log_file)
            total_stats["total_lines"] += stats["total_lines"]
            total_stats["errors"] += stats["errors"]
            total_stats["warnings"] += stats["warnings"]
            total_stats["success"] += stats["success"]
        
        # Count posts/messages from inbox
        if platform.lower() in ["whatsapp", "gmail"]:
            total_stats["messages"] = self._count_files_in_dir(self.inbox_dir, prefix=platform.lower())
        elif platform.lower() in ["facebook", "instagram", "twitter"]:
            # Count from audit logs
            audit_file = os.path.join(self.log_dir, f"{platform.lower()}_audit.jsonl")
            if os.path.exists(audit_file):
                with open(audit_file, 'r') as f:
                    total_stats["posts"] = sum(1 for line in f if '"success": true' in line)
        
        return total_stats
    
    def generate_weekly_report(self):
        """
        Generate weekly business audit report.
        
        Returns:
            dict: Weekly report data
        """
        self._log("Generating weekly audit report...")
        
        start_of_week, end_of_week = self._get_week_range()
        
        # Collect stats from all platforms
        platforms = {
            "Facebook": self._collect_platform_stats("Facebook"),
            "Instagram": self._collect_platform_stats("Instagram"),
            "Twitter/X": self._collect_platform_stats("Twitter"),
            "WhatsApp": self._collect_platform_stats("WhatsApp"),
            "Gmail": self._collect_platform_stats("Gmail"),
        }
        
        # Calculate totals
        total_posts = sum(p.get("posts", 0) for p in platforms.values())
        total_messages = sum(p.get("messages", 0) for p in platforms.values())
        total_errors = sum(p.get("errors", 0) for p in platforms.values())
        total_success = sum(p.get("success", 0) for p in platforms.values())
        
        # Generate report
        report = {
            "report_type": "Weekly Business Audit",
            "generated_at": datetime.now().isoformat(),
            "week_start": start_of_week.strftime("%Y-%m-%d"),
            "week_end": end_of_week.strftime("%Y-%m-%d"),
            "summary": {
                "total_posts": total_posts,
                "total_messages": total_messages,
                "total_errors": total_errors,
                "total_successful_operations": total_success
            },
            "platforms": platforms,
            "health_score": self._calculate_health_score(total_errors, total_success)
        }
        
        # Save report
        self._save_report(report, "weekly_audit")
        
        self._log(f"Weekly report generated: {total_posts} posts, {total_messages} messages")
        
        return report
    
    def generate_ceo_briefing(self):
        """
        Generate CEO briefing document.
        
        Returns:
            str: Path to briefing document
        """
        self._log("Generating CEO briefing...")
        
        # Get weekly report
        weekly_report = self.generate_weekly_report()
        
        # Generate briefing content
        briefing = f"""# CEO Weekly Briefing

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Period:** {weekly_report['week_start']} to {weekly_report['week_end']}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Social Posts | {weekly_report['summary']['total_posts']} |
| Total Messages | {weekly_report['summary']['total_messages']} |
| System Errors | {weekly_report['summary']['total_errors']} |
| Health Score | {weekly_report['health_score']}/100 |

---

## Platform Performance

### Social Media
| Platform | Posts | Errors | Status |
|----------|-------|--------|--------|
| Facebook | {weekly_report['platforms']['Facebook'].get('posts', 0)} | {weekly_report['platforms']['Facebook'].get('errors', 0)} | {'✅' if weekly_report['platforms']['Facebook'].get('errors', 0) == 0 else '⚠️'} |
| Instagram | {weekly_report['platforms']['Instagram'].get('posts', 0)} | {weekly_report['platforms']['Instagram'].get('errors', 0)} | {'✅' if weekly_report['platforms']['Instagram'].get('errors', 0) == 0 else '⚠️'} |
| Twitter/X | {weekly_report['platforms']['Twitter/X'].get('posts', 0)} | {weekly_report['platforms']['Twitter/X'].get('errors', 0)} | {'✅' if weekly_report['platforms']['Twitter/X'].get('errors', 0) == 0 else '⚠️'} |

### Communications
| Platform | Messages | Errors | Status |
|----------|----------|--------|--------|
| WhatsApp | {weekly_report['platforms']['WhatsApp'].get('messages', 0)} | {weekly_report['platforms']['WhatsApp'].get('errors', 0)} | {'✅' if weekly_report['platforms']['WhatsApp'].get('errors', 0) == 0 else '⚠️'} |
| Gmail | {weekly_report['platforms']['Gmail'].get('messages', 0)} | {weekly_report['platforms']['Gmail'].get('errors', 0)} | {'✅' if weekly_report['platforms']['Gmail'].get('errors', 0) == 0 else '⚠️'} |

---

## Key Highlights

- **Most Active Platform:** {self._get_most_active_platform(weekly_report)}
- **Total Operations:** {weekly_report['summary']['total_posts'] + weekly_report['summary']['total_messages']}
- **Error Rate:** {self._calculate_error_rate(weekly_report):.2f}%

---

## Action Items

1. {'✅ All systems operating normally' if weekly_report['summary']['total_errors'] == 0 else f'⚠️ {weekly_report["summary"]["total_errors"]} errors require attention'}
2. Review message inbox for pending responses
3. Plan next week's social media content

---

## Recommendations

{self._generate_recommendations(weekly_report)}

---

*Report generated by AI Employee Automation System - Gold Tier*
"""
        
        # Save briefing
        filename = f"CEO_Briefing_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        # Also update main CEO_Briefing.md
        main_briefing = os.path.join(self.log_dir, "..", "CEO_Briefing.md")
        try:
            with open(main_briefing, 'w', encoding='utf-8') as f:
                f.write(briefing)
        except:
            pass
        
        self._log(f"CEO briefing saved: {filepath}")
        
        return filepath
    
    def _calculate_health_score(self, errors, success):
        """Calculate system health score (0-100)."""
        total = errors + success
        if total == 0:
            return 100
        success_rate = (success / total) * 100
        return min(100, max(0, int(success_rate)))
    
    def _get_most_active_platform(self, report):
        """Get the most active platform."""
        max_activity = 0
        most_active = "N/A"
        
        for platform, stats in report['platforms'].items():
            activity = stats.get('posts', 0) + stats.get('messages', 0)
            if activity > max_activity:
                max_activity = activity
                most_active = platform
        
        return most_active
    
    def _calculate_error_rate(self, report):
        """Calculate error rate percentage."""
        total_ops = report['summary']['total_posts'] + report['summary']['total_messages']
        if total_ops == 0:
            return 0.0
        return (report['summary']['total_errors'] / total_ops) * 100
    
    def _generate_recommendations(self, report):
        """Generate recommendations based on report data."""
        recommendations = []
        
        if report['summary']['total_errors'] > 5:
            recommendations.append("- **High error count:** Review system logs and consider increasing retry attempts")
        
        if report['summary']['total_posts'] < 3:
            recommendations.append("- **Low posting activity:** Consider increasing social media engagement")
        
        if report['summary']['total_messages'] > 20:
            recommendations.append("- **High message volume:** Consider implementing auto-response for common queries")
        
        if report['health_score'] < 80:
            recommendations.append("- **System health below target:** Schedule maintenance review")
        
        if not recommendations:
            recommendations.append("- System operating within normal parameters")
            recommendations.append("- Continue current automation schedule")
        
        return "\n".join(recommendations)
    
    def _save_report(self, report, report_type):
        """Save report to file."""
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self._log(f"Report saved: {filepath}")


if __name__ == "__main__":
    print("Weekly Audit Skill - Test Mode")
    print("=" * 50)
    
    audit = WeeklyAuditSkill()
    
    # Generate weekly report
    report = audit.generate_weekly_report()
    print("\nWeekly Report Summary:")
    print(f"  Posts: {report['summary']['total_posts']}")
    print(f"  Messages: {report['summary']['total_messages']}")
    print(f"  Health Score: {report['health_score']}/100")
    
    # Generate CEO briefing
    briefing_path = audit.generate_ceo_briefing()
    print(f"\nCEO Briefing saved to: {briefing_path}")
