#!/usr/bin/env python3
"""
Base Watcher - Gold Tier
========================
Abstract base class for all watchers
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "Logs"
INBOX_DIR = BASE_DIR / "Inbox"
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"

# Create directories
LOGS_DIR.mkdir(parents=True, exist_ok=True)
INBOX_DIR.mkdir(parents=True, exist_ok=True)
NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'watchers.log'),
        logging.StreamHandler()
    ]
)


class BaseWatcher(ABC):
    """Abstract base class for all watchers"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_items = set()
        
    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
    
    def run(self):
        """Main watcher loop"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Inbox: {INBOX_DIR}')
        self.logger.info(f'Needs Action: {NEEDS_ACTION_DIR}')
        
        while True:
            try:
                items = self.check_for_updates()
                
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath.name}')
                
                if items:
                    self.logger.info(f'Processed {len(items)} items')
                
            except KeyboardInterrupt:
                self.logger.info('Stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error: {e}', exc_info=True)
            
            time.sleep(self.check_interval)
