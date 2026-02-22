#!/usr/bin/env python3
"""
AI Orchestrator - Gold Tier (Updated)
======================================
Cross-domain message orchestration with Ralph Wiggum loop.

Domains:
- Personal: Gmail, WhatsApp
- Business: LinkedIn, Facebook, Instagram, X (Twitter)

Gold Tier Features:
- Read from Inbox, classify messages (personal/business)
- Route to correct watcher/poster script via subprocess
- Ralph Wiggum loop: iterate until TASK_COMPLETE
- Error recovery: retry 3 times with exponential backoff
- Audit logging to Audit_Log.md with timestamps
- Human-in-the-loop for sensitive actions
- Weekly audit trigger

Agent Skills:
- Cross-domain routing
- Error recovery with graceful skip
- Comprehensive audit logging
- Human-in-the-loop confirmation
- Ralph Wiggum iterative completion
"""

import os
# Human-in-the-loop override
AUTO_CONFIRM = os.getenv("AUTO_CONFIRM", "false").lower() == "true"

import subprocess
import json
import os
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Configuration
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"
AUDIT_LOG = BASE_DIR / "Audit_Log.md"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RALPH_WIGGUM_MAX_ITERATIONS = 10
WEEKLY_AUDIT_INTERVAL = 7 * 24 * 60 * 60  # 7 days in seconds

# Domain classification
PERSONAL_DOMAINS = ['gmail', 'whatsapp', 'personal']
BUSINESS_DOMAINS = ['linkedin', 'facebook', 'instagram', 'twitter', 'x', 'business']

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AIOrchestrator')


class MessageType(Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    UNKNOWN = "unknown"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


class AuditLogger:
    """Handles audit logging to Audit_Log.md"""
    
    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self._ensure_audit_log_exists()
    
    def _ensure_audit_log_exists(self):
        """Create audit log file if it doesn't exist"""
        if not self.audit_log_path.exists():
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.audit_log_path, 'w') as f:
                f.write("# Audit Log\n\n")
                f.write("## Gold Tier AI Orchestrator Audit Trail\n\n")
                f.write("---\n\n")
    
    def log(self, event_type: str, details: str, status: str = "INFO"):
        """Log an audit event with timestamp"""
        timestamp = datetime.now().isoformat()
        with open(self.audit_log_path, 'a') as f:
            f.write(f"### [{timestamp}] {status}: {event_type}\n\n")
            f.write(f"{details}\n\n")
            f.write("---\n\n")
    
    def log_task(self, task_id: str, action: str, domain: str, status: str, details: str = ""):
        """Log a task execution with full audit trail"""
        timestamp = datetime.now().isoformat()
        with open(self.audit_log_path, 'a') as f:
            f.write(f"### [{timestamp}] TASK: {task_id}\n\n")
            f.write(f"- **Action**: {action}\n")
            f.write(f"- **Domain**: {domain}\n")
            f.write(f"- **Status**: {status}\n")
            if details:
                f.write(f"- **Details**: {details}\n")
            f.write("\n---\n\n")
    
    def log_error(self, task_id: str, error: str, attempt: int, max_attempts: int):
        """Log error with retry information"""
        timestamp = datetime.now().isoformat()
        with open(self.audit_log_path, 'a') as f:
            f.write(f"### [{timestamp}] ERROR: {task_id}\n\n")
            f.write(f"- **Error**: {error}\n")
            f.write(f"- **Attempt**: {attempt}/{max_attempts}\n")
            f.write(f"- **Action**: {'Retrying' if attempt < max_attempts else 'Skipping gracefully'}\n\n")
            f.write("---\n\n")
    
    def log_human_decision(self, task_id: str, action: str, confirmed: bool):
        """Log human-in-the-loop decision"""
        timestamp = datetime.now().isoformat()
        status = "CONFIRMED" if confirmed else "DENIED"
        with open(self.audit_log_path, 'a') as f:
            f.write(f"### [{timestamp}] HUMAN_DECISION: {task_id}\n\n")
            f.write(f"- **Action**: {action}\n")
            f.write(f"- **Decision**: {status}\n\n")
            f.write("---\n\n")
    
    def check_weekly_audit(self) -> bool:
        """Check if weekly audit is due"""
        if not self.audit_log_path.exists():
            return True
        
        last_modified = datetime.fromtimestamp(self.audit_log_path.stat().st_mtime)
        next_audit = last_modified + timedelta(seconds=WEEKLY_AUDIT_INTERVAL)
        
        if datetime.now() >= next_audit:
            self.log("WEEKLY_AUDIT_TRIGGER", 
                    f"Weekly audit triggered. Last audit: {last_modified.isoformat()}")
            return True
        return False
    
    def weekly_audit_summary(self, tasks_processed: int, errors: int, success_rate: float):
        """Log weekly audit summary"""
        timestamp = datetime.now().isoformat()
        with open(self.audit_log_path, 'a') as f:
            f.write(f"## Weekly Audit Summary - {timestamp}\n\n")
            f.write(f"- **Tasks Processed**: {tasks_processed}\n")
            f.write(f"- **Errors**: {errors}\n")
            f.write(f"- **Success Rate**: {success_rate:.2f}%\n")
            f.write(f"- **Status**: {'HEALTHY' if success_rate > 90 else 'REVIEW_NEEDED'}\n\n")
            f.write("---\n\n")


class MessageClassifier:
    """Classifies messages into personal or business domain"""
    
    def __init__(self):
        self.personal_keywords = ['family', 'friend', 'personal', 'home', 'vacation', 
                                  'birthday', 'party', 'dinner', 'casual']
        self.business_keywords = ['work', 'meeting', 'project', 'client', 'business',
                                  'proposal', 'contract', 'deadline', 'professional']
    
    def classify(self, message: Dict) -> MessageType:
        """Classify a message based on content and source"""
        source = message.get('source', '').lower()
        subject = message.get('subject', '').lower()
        content = message.get('content', '').lower()
        
        # Check source first
        for domain in PERSONAL_DOMAINS:
            if domain in source:
                return MessageType.PERSONAL
        
        for domain in BUSINESS_DOMAINS:
            if domain in source:
                return MessageType.BUSINESS
        
        # Check keywords
        text = f"{subject} {content}"
        personal_score = sum(1 for kw in self.personal_keywords if kw in text)
        business_score = sum(1 for kw in self.business_keywords if kw in text)
        
        if personal_score > business_score:
            return MessageType.PERSONAL
        elif business_score > personal_score:
            return MessageType.BUSINESS
        
        return MessageType.UNKNOWN


class HumanInTheLoop:
    """
    Agent Skill: Human-in-the-Loop Confirmation
    Requires human confirmation for sensitive actions
    
    Sensitive actions include:
    - Posting to social media (linkedin, facebook, instagram, twitter)
    - Login operations
    - Batch operations
    - Financial/revenue-related content
    - Account security changes
    - Delete operations
    """

    SENSITIVE_ACTIONS = [
        'login', 'batch_post', 'financial', 'account_change', 'delete',
        'post', 'linkedin', 'facebook', 'instagram', 'twitter', 'social'
    ]

    @staticmethod
    def is_sensitive(action: str) -> bool:
        """Check if action requires human confirmation"""
        action_lower = action.lower()
        return any(kw in action_lower for kw in HumanInTheLoop.SENSITIVE_ACTIONS)

    @staticmethod
    def confirm(action: str, details: str = "") -> bool:
        """
        Request human confirmation for sensitive action
        
        For posting actions, shows the content to be posted.
        For login actions, warns about credential usage.
        
        Returns: True if confirmed, False if denied
        """
        if AUTO_CONFIRM:
            logger.info(f"⚙️  AUTO_CONFIRM enabled - skipping confirmation for: {action}")
            return True

        if not HumanInTheLoop.is_sensitive(action):
            return True

        print("\n" + "=" * 60)
        print("⚠️  HUMAN APPROVAL REQUIRED")
        print("=" * 60)
        print(f"\n📋 Action: {action}")
        
        if details:
            print(f"\n📝 Details:")
            # Truncate long details for readability
            if len(details) > 500:
                print(f"   {details[:500]}...")
                print("   (content truncated)")
            else:
                print(f"   {details}")
        
        print("\n" + "-" * 60)
        response = input("\n✅ Approve this action? (yes/no): ").strip().lower()
        confirmed = response in ['yes', 'y', 'ye']
        
        if confirmed:
            print("✅ Action APPROVED - proceeding...")
        else:
            print("❌ Action DENIED - skipping...")
        
        print("=" * 60 + "\n")

        return confirmed


class ScriptRunner:
    """Runs watcher/poster scripts via subprocess"""
    
    def __init__(self, base_dir: Path, audit_logger: AuditLogger):
        self.base_dir = base_dir
        self.audit_logger = audit_logger
        self.human_loop = HumanInTheLoop()
    
    def run_script(self, script_path: str, args: List[str] = None, 
                   timeout: int = 300, task_id: str = "unknown") -> Tuple[bool, str, int]:
        """
        Run a script with retry logic and error logging
        
        Returns: (success, output, retry_count)
        """
        retries = 0
        last_error = None
        
        while retries < MAX_RETRIES:
            try:
                # Human-in-the-loop check for sensitive scripts
                if 'login' in script_path.lower() or 'poster' in script_path.lower():
                    if not self.human_loop.confirm("script_execution", f"Running: {script_path}"):
                        self.audit_logger.log_human_decision(task_id, "script_execution", False)
                        return False, "Human denied execution", 0
                
                cmd = ['python', script_path]
                if args:
                    cmd.extend(args)
                
                logger.info(f"Running script: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.base_dir
                )
                
                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"
                
                if result.returncode == 0:
                    return True, output, retries
                
                last_error = f"Script exited with code {result.returncode}"
                logger.warning(f"Script failed (attempt {retries + 1}/{MAX_RETRIES}): {last_error}")
                self.audit_logger.log_error(task_id, last_error, retries + 1, MAX_RETRIES)
                
            except subprocess.TimeoutExpired:
                last_error = "Script timed out"
                logger.warning(f"Script timeout (attempt {retries + 1}/{MAX_RETRIES})")
                self.audit_logger.log_error(task_id, last_error, retries + 1, MAX_RETRIES)
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Script error (attempt {retries + 1}/{MAX_RETRIES}): {last_error}")
                self.audit_logger.log_error(task_id, last_error, retries + 1, MAX_RETRIES)
            
            retries += 1
            if retries < MAX_RETRIES:
                delay = RETRY_DELAY * (2 ** (retries - 1))  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        # All retries exhausted - graceful skip
        logger.info(f"Gracefully skipping task {task_id} after {MAX_RETRIES} failed attempts")
        return False, last_error, retries # type: ignore


class RalphWiggumLoop:
    """
    Ralph Wiggum Loop: Iterates until TASK_COMPLETE
    "Me fail English? That's unpossible!" - Keeps trying until success
    
    Agent Skill: Strong Ralph Wiggum Loop
    - Tracks iterations with full audit logging
    - Logs each attempt to Audit_Log.md
    - Provides detailed failure analysis
    """
    
    def __init__(self, max_iterations: int = RALPH_WIGGUM_MAX_ITERATIONS, audit_logger: AuditLogger = None):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.task_status = TaskStatus.PENDING
        self.audit_logger = audit_logger
        self.task_id = None
    
    def start(self, task_id: str = None):
        """Start the loop with task tracking"""
        self.current_iteration = 0
        self.task_status = TaskStatus.IN_PROGRESS
        self.task_id = task_id
        logger.info("🍩 Ralph Wiggum Loop started - 'I'm gonna try real hard!'")
        if self.audit_logger and task_id:
            self.audit_logger.log("RALPH_WIGGUM_START", f"Task: {task_id}, Max iterations: {self.max_iterations}")
    
    def next_iteration(self) -> bool:
        """
        Move to next iteration
        
        Returns: True if can continue, False if max iterations reached
        """
        self.current_iteration += 1
        
        if self.current_iteration >= self.max_iterations:
            logger.warning(f"🍩 Ralph Wiggum Loop: Max iterations ({self.max_iterations}) reached")
            self.task_status = TaskStatus.FAILED
            if self.audit_logger and self.task_id:
                self.audit_logger.log("RALPH_WIGGUM_MAX", f"Task: {self.task_id}, Iterations: {self.current_iteration}")
            return False
        
        logger.info(f"🍩 Ralph Wiggum Loop: Iteration {self.current_iteration}/{self.max_iterations} - 'Me gonna try again!'")
        if self.audit_logger and self.task_id:
            self.audit_logger.log("RALPH_WIGGUM_ITERATION", f"Task: {self.task_id}, Iteration: {self.current_iteration}")
        return True
    
    def complete(self):
        """Mark task as complete"""
        self.task_status = TaskStatus.COMPLETE
        logger.info("🍩 Ralph Wiggum Loop: TASK_COMPLETE - 'I did it!'")
        if self.audit_logger and self.task_id:
            self.audit_logger.log("RALPH_WIGGUM_COMPLETE", f"Task: {self.task_id}, Iterations: {self.current_iteration}", "SUCCESS")
    
    def fail(self, reason: str = ""):
        """Mark task as failed"""
        self.task_status = TaskStatus.FAILED
        logger.error(f"🍩 Ralph Wiggum Loop: TASK_FAILED - 'Me fail?' Reason: {reason}")
        if self.audit_logger and self.task_id:
            self.audit_logger.log("RALPH_WIGGUM_FAIL", f"Task: {self.task_id}, Reason: {reason}", "FAILED")
    
    def is_complete(self) -> bool:
        return self.task_status == TaskStatus.COMPLETE
    
    def is_failed(self) -> bool:
        return self.task_status == TaskStatus.FAILED


class AIOrchestrator:
    """
    Gold Tier AI Orchestrator (Updated)
    
    Cross-domain message orchestration with:
    - Personal domain: Gmail, WhatsApp
    - Business domain: LinkedIn, Facebook, Instagram, X
    - Error recovery with 3 retries
    - Full audit logging to Audit_Log.md
    - Human-in-the-loop for sensitive actions
    - Strong Ralph Wiggum loop
    """
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.audit_logger = AuditLogger(AUDIT_LOG)
        self.classifier = MessageClassifier()
        self.script_runner = ScriptRunner(self.base_dir, self.audit_logger)
        self.ralph_loop = RalphWiggumLoop(audit_logger=self.audit_logger)
        self.human_loop = HumanInTheLoop()
        
        # Script mappings
        self.personal_scripts = {
            'gmail': str(self.base_dir / 'Watchers' / 'gmail_watcher.py'),
            'whatsapp': str(self.base_dir / 'WhatsApp' / 'whatsapp_watcher.py'),
        }
        
        self.business_scripts = {
            'linkedin': str(self.base_dir / 'LinkedIn' / 'linkedin_watcher.py'),
            'facebook': str(self.base_dir / 'Watchers' / 'facebook_watcher.py'),
            'instagram': str(self.base_dir / 'Watchers' / 'instagram_watcher.py'),
            'twitter': str(self.base_dir / 'Watchers' / 'twitter_watcher.py'),
            'x': str(self.base_dir / 'Watchers' / 'twitter_watcher.py'),
        }
        
        # Metrics
        self.tasks_processed = 0
        self.errors = 0
        
        logger.info("🤖 Gold Tier AI Orchestrator initialized")
        self.audit_logger.log("ORCHESTRATOR_START", "Gold Tier AI Orchestrator initialized")
    
    def read_inbox(self) -> List[Dict]:
        """Read messages from inbox directory"""
        messages = []
        
        if not INBOX_DIR.exists():
            logger.warning(f"Inbox directory not found: {INBOX_DIR}")
            return messages
        
        for msg_file in INBOX_DIR.glob('*.json'):
            try:
                with open(msg_file, 'r') as f:
                    message = json.load(f)
                    message['_file'] = str(msg_file)
                    messages.append(message)
            except Exception as e:
                logger.error(f"Error reading {msg_file}: {e}")
        
        logger.info(f"Read {len(messages)} messages from inbox")
        return messages
    
    def get_script_for_message(self, message: Dict, msg_type: MessageType) -> Optional[str]:
        """Get the appropriate script for a message"""
        source = message.get('source', '').lower()
        
        if msg_type == MessageType.PERSONAL:
            for domain, script in self.personal_scripts.items():
                if domain in source:
                    return script
            # Default to WhatsApp for personal
            return self.personal_scripts.get('whatsapp')
        
        elif msg_type == MessageType.BUSINESS:
            for domain, script in self.business_scripts.items():
                if domain in source:
                    return script
            # Default to LinkedIn for business
            return self.business_scripts.get('linkedin')
        
        return None
    
    def process_message(self, message: Dict) -> bool:
        """Process a single message through the Ralph Wiggum Loop"""
        task_id = message.get('id', f"task_{self.tasks_processed}")
        
        # Human-in-the-loop for batch operations
        if self.human_loop.is_sensitive('batch_post') and not AUTO_CONFIRM:
            if not self.human_loop.confirm('process_message', f"Processing message: {task_id}"):
                self.audit_logger.log_human_decision(task_id, 'process_message', False)
                self.errors += 1
                return False
        
        # Classify message
        msg_type = self.classifier.classify(message)
        logger.info(f"Message {task_id} classified as: {msg_type.value}")
        self.audit_logger.log("MESSAGE_CLASSIFIED", f"Task: {task_id}, Type: {msg_type.value}")
        
        # Get appropriate script
        script_path = self.get_script_for_message(message, msg_type)
        
        if not script_path:
            logger.error(f"No script found for message {task_id}")
            self.audit_logger.log_task(task_id, "CLASSIFY", "unknown", "FAILED", 
                                      "No matching script found")
            self.errors += 1
            return False
        
        # Determine domain
        domain = "personal" if msg_type == MessageType.PERSONAL else "business"
        
        # Start Ralph Wiggum Loop with task tracking
        self.ralph_loop.start(task_id)
        
        while self.ralph_loop.next_iteration():
            # Run the script
            success, output, retries = self.script_runner.run_script(
                script_path,
                args=['--message', json.dumps(message)],
                task_id=task_id
            )
            
            if success:
                self.ralph_loop.complete()
                self.audit_logger.log_task(task_id, "PROCESS", domain, "SUCCESS",
                                          f"Script: {script_path}, Retries: {retries}")
                self.tasks_processed += 1
                return True
            
            logger.warning(f"Iteration {self.ralph_loop.current_iteration} failed")
        
        # Ralph Wiggum Loop exhausted - graceful skip
        self.ralph_loop.fail(f"Max iterations exhausted for {task_id}")
        self.audit_logger.log_task(task_id, "PROCESS", domain, "FAILED",
                                  f"Ralph Wiggum Loop exhausted after {self.ralph_loop.current_iteration} iterations - gracefully skipped")
        self.errors += 1
        return False
    
    def run(self) -> Dict:
        """Main orchestration loop"""
        logger.info("🚀 Starting Gold Tier AI Orchestrator")
        
        # Check weekly audit
        if self.audit_logger.check_weekly_audit():
            logger.info("📊 Weekly audit triggered")
        
        # Read inbox
        messages = self.read_inbox()
        
        if not messages:
            logger.info("No messages to process")
            return {"processed": 0, "errors": 0, "success_rate": 100.0}
        
        # Process each message
        for message in messages:
            self.process_message(message)
        
        # Calculate metrics
        total = self.tasks_processed + self.errors
        success_rate = (self.tasks_processed / total * 100) if total > 0 else 100.0
        
        result = {
            "processed": self.tasks_processed,
            "errors": self.errors,
            "success_rate": success_rate
        }
        
        logger.info(f"✅ Orchestration complete: {result}")
        
        # Log weekly audit summary if triggered
        if self.audit_logger.check_weekly_audit():
            self.audit_logger.weekly_audit_summary(
                self.tasks_processed,
                self.errors,
                success_rate
            )
        
        return result
    
    def run_single_task(self, task: Dict) -> bool:
        """Run a single task (for external triggers)"""
        return self.process_message(task)


def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 Gold Tier AI Orchestrator (Updated)")
    print("=" * 60)
    print()
    print("Gold Tier Features:")
    print("  📱 Cross-domain: Gmail/WhatsApp (personal)")
    print("     💼 LinkedIn/FB/IG/X (business)")
    print("  🍩 Ralph Wiggum Loop (iterate until TASK_COMPLETE)")
    print("  🔄 Error Recovery (3 retries with exponential backoff)")
    print("  📋 Audit Logging (Audit_Log.md with timestamps)")
    print("  👤 Human-in-the-Loop (sensitive action confirmation)")
    print("  📊 Weekly Audit Trigger")
    print()
    print("Environment:")
    print(f"  AUTO_CONFIRM: {AUTO_CONFIRM}")
    print()
    print("=" * 60)
    print()
    
    orchestrator = AIOrchestrator()
    result = orchestrator.run()
    
    print()
    print("=" * 60)
    print("📊 Results:")
    print(f"  Tasks Processed: {result['processed']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Success Rate: {result['success_rate']:.2f}%")
    print(f"  Audit Log: {AUDIT_LOG}")
    print("=" * 60)
    
    return 0 if result['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
