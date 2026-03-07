"""
Scheduler module for running daily LOF arbitrage monitoring tasks.
"""

import logging
import schedule
import time
import pytz
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class DailyScheduler:
    """Scheduler for running daily tasks at specified time."""
    
    def __init__(self, hour: int = 13, minute: int = 0, timezone: str = "Asia/Shanghai"):
        """
        Initialize scheduler.
        
        Args:
            hour: Hour to run task (24-hour format). Defaults to 13.
            minute: Minute to run task. Defaults to 0.
            timezone: Timezone for scheduling. Defaults to Asia/Shanghai.
        """
        self.hour = hour
        self.minute = minute
        self.timezone = pytz.timezone(timezone)
        self.task: Optional[Callable] = None
        self.running = False
        
        logger.info(f"DailyScheduler initialized for {hour:02d}:{minute:02d} {timezone}")
    
    def set_task(self, task: Callable) -> 'DailyScheduler':
        """
        Set the task to be executed daily.
        
        Args:
            task: Callable to execute.
            
        Returns:
            Self for method chaining.
        """
        self.task = task
        schedule.every().day.at(f"{self.hour:02d}:{self.minute:02d}").do(self._run_task)
        logger.info(f"Task scheduled for {self.hour:02d}:{self.minute:02d}")
        return self
    
    def _run_task(self):
        """Wrapper to run the task with error handling."""
        if self.task is None:
            logger.warning("No task configured")
            return
        
        logger.info(f"Running scheduled task at {datetime.now(self.timezone)}")
        try:
            self.task()
            logger.info("Scheduled task completed successfully")
        except Exception as e:
            logger.error(f"Scheduled task failed: {e}", exc_info=True)
    
    def run_now(self) -> bool:
        """
        Run the task immediately.
        
        Returns:
            bool: True if task ran successfully, False otherwise.
        """
        if self.task is None:
            logger.warning("No task configured")
            return False
        
        try:
            self.task()
            return True
        except Exception as e:
            logger.error(f"Immediate task execution failed: {e}", exc_info=True)
            return False
    
    def start(self):
        """Start the scheduler loop."""
        self.running = True
        logger.info("Scheduler started")
        
        # Run pending jobs immediately if any
        schedule.run_pending()
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler loop."""
        self.running = False
        logger.info("Scheduler stopped")
    
    def clear(self):
        """Clear all scheduled jobs."""
        schedule.clear()
        logger.info("All scheduled jobs cleared")
