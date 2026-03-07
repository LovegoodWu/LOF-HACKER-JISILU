"""
Test script for Feishu notification.

Usage:
    python tools/test_feishu.py     # Test Feishu notification
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from notifier.feishu_notifier import FeishuNotifier


def main():
    """Test Feishu notification."""
    print("=" * 50)
    print("LOF Hacker - Feishu Notification Test")
    print("=" * 50)
    
    # Check configuration
    if not settings.FEISHU_ENABLED:
        print("✗ Feishu notification is not enabled (FEISHU_ENABLED=false)")
        print("  Please set FEISHU_ENABLED=true in your .env file")
        sys.exit(1)
    
    if not settings.FEISHU_WEBHOOK_URL:
        print("✗ Feishu webhook URL is not configured")
        print("  Please set FEISHU_WEBHOOK_URL in your .env file")
        sys.exit(1)
    
    print(f"✓ Feishu enabled: {settings.FEISHU_ENABLED}")
    print(f"✓ Webhook URL: {settings.FEISHU_WEBHOOK_URL[:50]}...")
    print(f"✓ Message type: {settings.FEISHU_MESSAGE_TYPE}")
    print()
    
    # Send test message
    print("Sending test message...")
    notifier = FeishuNotifier()
    
    if notifier.send_test_message():
        print("\n✓ Test message sent successfully!")
        print("  Please check your Feishu group chat for the message.")
        sys.exit(0)
    else:
        print("\n✗ Failed to send test message.")
        print("  Check logs/app.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
