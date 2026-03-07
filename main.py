"""
LOF Arbitrage Monitor - Main Entry Point

A tool for monitoring LOF arbitrage opportunities from jishilu.cn
and sending notifications via email and Feishu.

Usage:
    python main.py              # Run once immediately
    python main.py --schedule   # Run as scheduled task (daily at 13:00)
    python main.py --test       # Send test notifications
"""

import argparse
import sys
from datetime import datetime

from config.settings import settings
from utils.logger import setup_logging
from scraper.jisilu import JisiluScraper
from filter.arbitrage_filter import ArbitrageFilter
from notifier.email_notifier import EmailNotifier
from notifier.feishu_notifier import FeishuNotifier
from scheduler.daily_job import DailyScheduler


def run_arbitrage_monitor() -> bool:
    """
    Run the LOF arbitrage monitoring workflow.
    
    Returns:
        bool: True if completed successfully, False otherwise.
    """
    logger = __import__('logging').getLogger(__name__)
    logger.info("=" * 50)
    logger.info(f"Starting LOF Arbitrage Monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Validate settings
        missing = settings.validate()
        if missing:
            logger.error(f"Missing required settings: {', '.join(missing)}")
            logger.error("Please check your .env file")
            return False
        
        # Step 2: Login and fetch data
        scraper = JisiluScraper()
        try:
            # Skip login if already logged in via saved cookies
            if not scraper.is_logged_in:
                if not scraper.login():
                    logger.error("Failed to login to jishilu.cn")
                    return False
            
            lof_data = scraper.fetch_lof_arbitrage_data()
            if not lof_data:
                logger.warning("No LOF data fetched")
                return False
            
            logger.info(f"Fetched {len(lof_data)} LOF records")
        finally:
            scraper.close()
        
        # Step 3: Filter arbitrage opportunities
        filter_engine = ArbitrageFilter()
        opportunities = filter_engine.filter(lof_data)
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        
        # Step 4: Send notifications (email and/or Feishu)
        notification_sent = False
        
        # Send email notification
        if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
            email_notifier = EmailNotifier()
            
            if opportunities:
                opportunities_html = filter_engine.format_for_email(opportunities)
                email_success = email_notifier.send_arbitrage_alert(opportunities_html, len(opportunities))
            else:
                opportunities_html = "<p>未发现符合条件的套利机会</p>"
                email_success = email_notifier.send_arbitrage_alert(opportunities_html, 0)
            
            if email_success:
                logger.info("Email notification sent successfully")
                notification_sent = True
            else:
                logger.error("Failed to send email notification")
        
        # Send Feishu notification
        if settings.FEISHU_ENABLED and settings.FEISHU_WEBHOOK_URL:
            feishu_notifier = FeishuNotifier()
            feishu_success = feishu_notifier.send_arbitrage_alert(opportunities, len(opportunities))
            
            if feishu_success:
                logger.info("Feishu notification sent successfully")
                notification_sent = True
            else:
                logger.error("Failed to send Feishu notification")
        
        if not notification_sent:
            logger.warning("No notifications were sent")
        
        logger.info("LOF Arbitrage Monitor completed")
        logger.info("=" * 50)
        return notification_sent
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LOF Arbitrage Monitor - Monitor LOF arbitrage opportunities from jishilu.cn"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run as scheduled task (daily at 13:00)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Send test email"
    )
    
    args = parser.parse_args()
    
    # Setup logging (only once at the beginning)
    setup_logging()
    logger = __import__('logging').getLogger(__name__)
    
    if args.test:
        # Test notification functionality
        logger.info("Sending test notifications...")
        all_success = True
        
        # Test email
        if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
            logger.info("Testing email notification...")
            email_notifier = EmailNotifier()
            if email_notifier.send_test_email():
                print("✓ Test email sent successfully!")
            else:
                print("✗ Failed to send test email. Check logs for details.")
                all_success = False
        else:
            print("⊘ Email notification not configured (skipped)")
        
        # Test Feishu
        if settings.FEISHU_ENABLED and settings.FEISHU_WEBHOOK_URL:
            logger.info("Testing Feishu notification...")
            feishu_notifier = FeishuNotifier()
            if feishu_notifier.send_test_message():
                print("✓ Test Feishu message sent successfully!")
            else:
                print("✗ Failed to send test Feishu message. Check logs for details.")
                all_success = False
        else:
            print("⊘ Feishu notification not configured (skipped)")
        
        sys.exit(0 if all_success else 1)
    
    elif args.schedule:
        # Run as scheduled task
        logger.info("Starting LOF Arbitrage Monitor in scheduled mode")
        
        scheduler = DailyScheduler(
            hour=settings.SCHEDULE_HOUR,
            minute=settings.SCHEDULE_MINUTE
        )
        scheduler.set_task(run_arbitrage_monitor)
        
        print(f"Scheduler started. Task will run daily at {settings.SCHEDULE_HOUR:02d}:{settings.SCHEDULE_MINUTE:02d}")
        print("Press Ctrl+C to stop.")
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            scheduler.stop()
            print("\nScheduler stopped.")
    
    else:
        # Run once immediately
        logger.info("Running LOF Arbitrage Monitor once")
        success = run_arbitrage_monitor()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
