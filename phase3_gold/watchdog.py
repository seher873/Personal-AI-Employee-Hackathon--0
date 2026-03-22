#!/usr/bin/env python3
"""
Watchdog Process Monitor - Gold Tier
=====================================
Monitor and restart critical processes automatically

Features:
- Auto-restart failed watchers
- Log all restarts
- Notify human on restart
- PID file tracking
"""

import subprocess
import time
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
PHASE3_DIR = Path(__file__).parent
LOGS_DIR = PHASE3_DIR / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Process timeout in seconds
CHECK_INTERVAL = 60  # Check every 60 seconds
MAX_RESTARTS_PER_HOUR = 3  # Prevent infinite restart loops

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Watchdog')


class ProcessInfo:
    """Track process information"""
    def __init__(self, name: str, cmd: str, pid_file: Path):
        self.name = name
        self.cmd = cmd
        self.pid_file = pid_file
        self.pid = None
        self.process = None
        self.restart_count = 0
        self.last_restart = None

    def __repr__(self):
        return f"ProcessInfo({self.name}, pid={self.pid}, running={self.is_running()})"

    def is_running(self) -> bool:
        """Check if process is running"""
        if self.pid is None:
            return False

        try:
            # Windows: use tasklist
            import subprocess
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {self.pid}'],
                capture_output=True,
                text=True
            )
            return str(self.pid) in result.stdout
        except Exception:
            return False

    def start(self) -> bool:
        """Start the process"""
        try:
            # Split command for subprocess
            cmd_parts = self.cmd.split()

            # Start process in background
            self.process = subprocess.Popen(
                cmd_parts,
                cwd=str(PHASE3_DIR),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.pid = self.process.pid

            # Save PID to file
            self.pid_file.write_text(str(self.pid))

            logger.info(f"Started {self.name} (PID: {self.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start {self.name}: {e}")
            return False

    def stop(self):
        """Stop the process"""
        if self.process:
            try:
                if os.name == 'nt':
                    self.process.terminate()
                else:
                    self.process.kill()
                logger.info(f"Stopped {self.name}")
            except Exception as e:
                logger.error(f"Failed to stop {self.name}: {e}")


class WatchdogMonitor:
    """Monitor and restart critical processes"""

    def __init__(self):
        self.processes = {}
        self.restart_history = []  # Track restarts per hour
        self._setup_processes()

    def _setup_processes(self):
        """Setup processes to monitor"""
        process_configs = {
            'gmail_watcher': 'py Watchers/watcher_gmail.py',
            'whatsapp_watcher': 'py Watchers/watcher_whatsapp.py',
            'linkedin_watcher': 'py Watchers/watcher_linkedin.py',
        }

        for name, cmd in process_configs.items():
            pid_file = LOGS_DIR / f'{name}.pid'
            self.processes[name] = ProcessInfo(name, cmd, pid_file)

        logger.info(f"Watchdog monitoring {len(self.processes)} processes")

    def _can_restart(self, process: ProcessInfo) -> bool:
        """Check if process can be restarted (rate limiting)"""
        now = datetime.now()

        # Clean old history (older than 1 hour)
        one_hour_ago = now.timestamp() - 3600
        self.restart_history = [
            ts for ts in self.restart_history
            if ts > one_hour_ago
        ]

        # Check if this process exceeded restart limit
        recent_restarts = len(self.restart_history)
        if recent_restarts >= MAX_RESTARTS_PER_HOUR:
            logger.warning(
                f"Max restarts per hour reached ({MAX_RESTARTS_PER_HOUR}). "
                f"Not restarting {process.name}"
            )
            return False

        return True

    def _record_restart(self, process: ProcessInfo):
        """Record restart for rate limiting"""
        self.restart_history.append(datetime.now().timestamp())
        process.restart_count += 1
        process.last_restart = datetime.now()

    def _notify_human(self, process: ProcessInfo):
        """Notify human that process was restarted"""
        notification_file = LOGS_DIR / f'WATCHDOG_NOTIFICATION_{process.name}.md'

        content = f"""---
type: watchdog_notification
process: {process.name}
timestamp: {datetime.now().isoformat()}
restart_count: {process.restart_count}
---

# Process Auto-Restarted

**Process:** {process.name}

**Restarted at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total restarts (session):** {process.restart_count}

**Command:** `{process.cmd}`

---

This is an automated notification. The watchdog detected that the process
was not running and restarted it automatically.

If this happens frequently, investigate:
1. Check logs: `Logs/watchdog.log`
2. Check process logs: `Logs/{process.name}*.log`
3. Consider manual intervention if restarts continue
"""

        notification_file.write_text(content, encoding='utf-8')
        logger.info(f"Notification saved: {notification_file.name}")

    def check_and_restart(self):
        """Check all processes and restart if needed"""
        logger.debug("Checking processes...")

        for name, process in self.processes.items():
            if not process.is_running():
                logger.warning(f"{name} is not running")

                # Check rate limiting
                if not self._can_restart(process):
                    continue

                # Attempt restart
                logger.warning(f"{name} not running, restarting...")

                if process.start():
                    self._record_restart(process)
                    self._notify_human(process)
                    logger.info(f"Successfully restarted {name}")
                else:
                    logger.error(f"Failed to restart {name}")
            else:
                logger.debug(f"{name} is running (PID: {process.pid})")

    def run(self):
        """Main watchdog loop"""
        logger.info("=" * 60)
        logger.info("Watchdog Process Monitor Started")
        logger.info("=" * 60)
        logger.info(f"Monitoring {len(self.processes)} processes:")
        for name, process in self.processes.items():
            logger.info(f"  - {name}: {process.cmd}")
        logger.info(f"Check interval: {CHECK_INTERVAL}s")
        logger.info(f"Max restarts/hour: {MAX_RESTARTS_PER_HOUR}")
        logger.info("=" * 60)

        try:
            while True:
                self.check_and_restart()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Watchdog stopped by user")
            # Stop all processes
            for process in self.processes.values():
                process.stop()
        except Exception as e:
            logger.error(f"Watchdog error: {e}", exc_info=True)
            raise


def main():
    """Entry point"""
    watchdog = WatchdogMonitor()
    watchdog.run()


if __name__ == '__main__':
    main()
