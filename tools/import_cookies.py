#!/usr/bin/env python3
"""
Cookie import utility for LOF Hacker.

This script helps you import cookies from browser export files.

Usage:
    python tools/import_cookies.py <path_to_json_file>

Example:
    python tools/import_cookies.py ~/Downloads/jisilu_cookies.json
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.jisilu import JisiluScraper


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Please provide the path to the JSON cookie file")
        print("\nExample:")
        print("  python tools/import_cookies.py ~/Downloads/jisilu_cookies.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    print(f"Importing cookies from: {json_file}")
    
    scraper = JisiluScraper(use_saved_cookies=False)
    
    if scraper.import_cookies_from_json(json_file):
        print("\n✓ Cookies imported successfully!")
        print("✓ You are now logged in to jisilu.cn")
        print("\nCookies saved to: data/.jisilu_cookies.json")
    else:
        print("\n✗ Failed to import cookies")
        print("  The cookies may be expired or invalid")
        print("  Please try logging in again and exporting fresh cookies")
        sys.exit(1)


if __name__ == "__main__":
    main()
