#!/usr/bin/env python
"""
Test script to verify automatic login when cookies expire.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.jisilu import JisiluScraper, COOKIE_JSON_FILE

def test_auto_login():
    """Test automatic login when cookies expire."""
    print("=" * 60)
    print("Testing automatic login when cookies expire")
    print("=" * 60)
    
    # Step 1: Create scraper with saved cookies
    print("\n[Step 1] Creating scraper with saved cookies...")
    scraper = JisiluScraper(use_saved_cookies=True)
    
    # Step 2: Check if cookies exist
    print("\n[Step 2] Checking cookie file...")
    if os.path.exists(COOKIE_JSON_FILE):
        print(f"Cookie file exists: {COOKIE_JSON_FILE}")
        with open(COOKIE_JSON_FILE, 'r') as f:
            cookies = json.load(f)
        print(f"Number of cookies: {len(cookies)}")
        for cookie in cookies:
            print(f"  - {cookie.get('name')}: {cookie.get('value')[:20]}...")
    else:
        print(f"Cookie file not found: {COOKIE_JSON_FILE}")
    
    # Step 3: Check login status
    print("\n[Step 3] Checking login status...")
    print(f"is_logged_in: {scraper.is_logged_in}")
    
    # Step 4: Try to fetch data (this will trigger login if needed)
    print("\n[Step 4] Attempting to fetch LOF arbitrage data...")
    data = scraper.fetch_lof_arbitrage_data(only_limited=False)
    
    if data:
        print(f"✓ Successfully fetched {len(data)} LOF records")
        print("\nFirst record:")
        for key, value in list(data[0].items())[:5]:
            print(f"  {key}: {value}")
    else:
        print("✗ Failed to fetch data")
    
    # Step 5: Verify cookies were saved
    print("\n[Step 5] Verifying cookies after operation...")
    if os.path.exists(COOKIE_JSON_FILE):
        with open(COOKIE_JSON_FILE, 'r') as f:
            cookies = json.load(f)
        print(f"✓ Cookie file exists with {len(cookies)} cookies")
        
        # Check for critical cookies
        cookie_names = [c.get('name') for c in cookies]
        critical_cookies = ['kbzw__Session', 'kbzw__user_login']
        for name in critical_cookies:
            if name in cookie_names:
                print(f"  ✓ {name} present")
            else:
                print(f"  ✗ {name} MISSING")
    else:
        print("✗ Cookie file not found")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


def test_manual_cookie_expiration():
    """Test automatic login by manually expiring cookies."""
    print("=" * 60)
    print("Testing automatic login with manually expired cookies")
    print("=" * 60)
    
    # Step 1: Expire cookies manually
    print("\n[Step 1] Manually expiring cookies...")
    if os.path.exists(COOKIE_JSON_FILE):
        # Read current cookies
        with open(COOKIE_JSON_FILE, 'r') as f:
            cookies = json.load(f)
        
        # Modify session cookie to make it invalid
        for cookie in cookies:
            if cookie.get('name') == 'kbzw__Session':
                cookie['value'] = 'invalid_session_' + cookie.get('value', '')[-10:]
                break
        
        # Save modified cookies
        with open(COOKIE_JSON_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        print("✓ Cookies modified (session invalidated)")
    else:
        print("✗ Cookie file not found, cannot expire")
        return
    
    # Step 2: Create new scraper (should detect expired cookies and login)
    print("\n[Step 2] Creating new scraper (should auto-login)...")
    scraper = JisiluScraper(use_saved_cookies=True)
    
    # Step 3: Check if login was successful
    print("\n[Step 3] Checking login status...")
    print(f"is_logged_in: {scraper.is_logged_in}")
    
    # Step 4: Try to fetch data
    print("\n[Step 4] Attempting to fetch LOF arbitrage data...")
    data = scraper.fetch_lof_arbitrage_data(only_limited=False)
    
    if data:
        print(f"✓ Successfully fetched {len(data)} LOF records after auto-login")
    else:
        print("✗ Failed to fetch data after auto-login")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--expire':
        test_manual_cookie_expiration()
    else:
        test_auto_login()
