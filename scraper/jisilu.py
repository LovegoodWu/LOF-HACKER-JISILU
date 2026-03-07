"""
Jisilu.cn scraper module.
Handles login and data fetching for LOF arbitrage information.
Supports cookie persistence to avoid repeated logins.
"""

import logging
import json
import re
import time
import os
from typing import Optional
import requests
from config.settings import settings

logger = logging.getLogger(__name__)

# Cookie file path (JSON format only)
COOKIE_JSON_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', '.jisilu_cookies.json')


class JisiluScraper:
    """Scraper for jishilu.cn website."""
    
    def __init__(self, use_saved_cookies: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": settings.JISILU_HOME_URL,
            "X-Requested-With": "XMLHttpRequest",
        })
        self.is_logged_in = False
        self.cookie_json_file = COOKIE_JSON_FILE
        
        # Try to load saved cookies first
        if use_saved_cookies:
            if self.load_cookies():
                return
        
        logger.info("No valid cookies found, will attempt login when needed")
    
    def save_cookies(self) -> bool:
        """
        Save session cookies to file (JSON format).
        
        Returns:
            bool: True if saved successfully, False otherwise.
        """
        return self._save_cookies_to_json()
    
    def _save_cookies_to_json(self) -> bool:
        """
        Save session cookies to JSON file.
        
        Returns:
            bool: True if saved successfully, False otherwise.
        """
        try:
            cookies_list = []
            for cookie in self.session.cookies:
                cookies_list.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                })
            
            with open(self.cookie_json_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_list, f, indent=2)
            
            logger.info(f"Cookies saved to {self.cookie_json_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON cookies: {e}")
            return False
    
    def load_cookies(self) -> bool:
        """
        Load cookies from file (JSON format).
        
        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        # Try JSON format
        if os.path.exists(self.cookie_json_file):
            logger.info(f"Found JSON cookie file: {self.cookie_json_file}")
            if self._load_cookies_from_json():
                return True
        
        logger.debug("No saved cookies found")
        return False
    
    def _load_cookies_from_json(self) -> bool:
        """
        Load cookies from JSON file (browser export format).
        If cookies are expired, automatically attempt to login.
        
        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            with open(self.cookie_json_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Parse browser cookie format
            for cookie in cookies_data:
                name = cookie.get('name')
                value = cookie.get('value')
                domain = cookie.get('domain', '.jisilu.cn')
                path = cookie.get('path', '/')
                
                if name and value:
                    self.session.cookies.set(name, value, domain=domain, path=path)
            
            logger.info(f"Cookies loaded from {self.cookie_json_file}")
            
            # Verify cookies are still valid
            if self._verify_login():
                self.is_logged_in = True
                logger.info("Loaded cookies are valid, already logged in")
                return True
            else:
                logger.info("Loaded cookies are expired or invalid")
                self.session.cookies.clear()
                logger.info("Attempting to login with username/password...")
                # Try to login with credentials
                if self.login():
                    logger.info("Login successful, new cookies saved")
                    return True
                else:
                    logger.error("Login failed, cannot access data")
                    return False
        except Exception as e:
            logger.warning(f"Failed to load cookies from JSON: {e}")
            return False
    
    
    def import_cookies_from_json(self, json_file_path: str) -> bool:
        """
        Import cookies from a JSON file (browser export format).
        
        Args:
            json_file_path: Path to the JSON cookie file
            
        Returns:
            bool: True if imported successfully, False otherwise.
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Parse browser cookie format
            for cookie in cookies_data:
                name = cookie.get('name')
                value = cookie.get('value')
                domain = cookie.get('domain', '.jisilu.cn')
                path = cookie.get('path', '/')
                
                if name and value:
                    self.session.cookies.set(name, value, domain=domain, path=path)
            
            logger.info(f"Cookies imported from {json_file_path}")
            
            # Save cookies for future use
            self.save_cookies()
            
            # Verify cookies are still valid
            if self._verify_login():
                self.is_logged_in = True
                logger.info("Imported cookies are valid, already logged in")
                return True
            else:
                logger.warning("Imported cookies may be expired or invalid")
                return False
        except Exception as e:
            logger.error(f"Failed to import cookies: {e}")
            return False
    
    def _verify_login(self) -> bool:
        """
        Verify if the current session is logged in.
        
        Returns:
            bool: True if logged in, False otherwise.
        """
        try:
            response = self.session.get(
                settings.JISILU_LOF_ARB_LIST_URL,
                params={'___jsl': f'LST___t={int(time.time() * 1000)}', 'rp': 1},
                timeout=10
            )
            logger.debug(f"Verification response status: {response.status_code}")
            logger.debug(f"Verification response body: {response.text[:500]}")
            
            if response.status_code == 200:
                # Check if response is HTML (indicates error or not logged in)
                if response.text.strip().startswith('<!DOCTYPE') or response.text.strip().startswith('<html'):
                    logger.debug("Got HTML response instead of JSON, cookies may be invalid")
                    return False
                
                try:
                    result = response.json()
                    logger.debug(f"Verification response parsed: {result}")
                    
                    # If we get data rows, we're logged in
                    if result.get('rows'):
                        logger.debug("Got data rows, logged in")
                        return True
                    
                    # Check for guest restriction message (not logged in)
                    msg = result.get('msg', '')
                    logger.debug(f"Response message: {msg}")
                    
                    # Only return False if we explicitly see "not logged in" message
                    if '游客' in msg or '未登录' in msg:
                        logger.debug("Guest restriction detected, not logged in")
                        return False
                    
                    # For any other case (error but logged in, no data, etc.), assume logged in
                    # The actual data fetch will tell us if there's a real problem
                    logger.info(f"Verification inconclusive, assuming logged in: {result}")
                    return True
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON response: {e}")
                    return False
            
            logger.debug(f"Non-200 status code: {response.status_code}")
            # Even on non-200, assume cookies might still be valid
            return True
        except Exception as e:
            logger.debug(f"Login verification failed with exception: {e}")
            # On exception, assume cookies might still be valid
            return True
    
    def login(self, max_retries: int = 3, retry_delay: int = 60) -> bool:
        """
        Login to jisilu.cn using credentials from settings.
        
        Args:
            max_retries: Maximum number of retry attempts when rate-limited
            retry_delay: Delay in seconds between retries
            
        Returns:
            bool: True if login successful, False otherwise.
        """
        logger.info("Attempting to login to jisilu.cn...")
        
        # Check if encrypted credentials are configured
        if not settings.JISILU_ENCRYPTED_USERNAME or not settings.JISILU_ENCRYPTED_PASSWORD:
            logger.error("JISILU_ENCRYPTED_USERNAME or JISILU_ENCRYPTED_PASSWORD not configured")
            logger.error("Please note: Cookie file is the primary authentication method.")
            logger.error("Encrypted username/password is only a fallback.")
            logger.error("Get encrypted values from browser's login request payload.")
            return False
        
        for attempt in range(max_retries):
            try:
                # Prepare login data with encrypted credentials
                # The encrypted values are obtained from browser's login request
                # username: MD5 hash (32 characters)
                # password: AES-256 encrypted (64 characters)
                login_data = {
                    "return_url": settings.JISILU_HOME_URL,
                    "user_name": settings.JISILU_ENCRYPTED_USERNAME,
                    "password": settings.JISILU_ENCRYPTED_PASSWORD,
                    "auto_login": "1",  # Enable "remember me"
                    "aes": "1",  # Indicate password is AES encrypted
                }
                
                # Post login request
                response = self.session.post(
                    settings.JISILU_LOGIN_URL,
                    data=login_data,
                    timeout=30,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Parse response
                login_successful = False
                try:
                    result = response.json()
                    logger.debug(f"Login response: {result}")
                    
                    # Check for success (code == 200)
                    if result.get('code') == 200:
                        login_successful = True
                        logger.info("Login successful (code=200)!")
                    else:
                        # Login failed, print response for debugging
                        logger.error(f"Login failed: {result}")
                        self.is_logged_in = False
                        return False
                except json.JSONDecodeError:
                    # Response is not JSON, check HTML content
                    logger.warning("Login response is not JSON, checking HTML content...")
                    # Check for logout link in HTML (indicates logged in state)
                    if "logout" in response.text.lower():
                        login_successful = True
                        logger.info("Login successful (HTML content indicates success)!")
                
                if login_successful:
                    self.is_logged_in = True
                    # Save cookies after successful login
                    if self.save_cookies():
                        logger.info("Login cookies saved successfully")
                        # Verify saved cookies work
                        if self._verify_login():
                            logger.info("Saved cookies verified successfully")
                            return True
                        else:
                            logger.warning("Saved cookies may not be valid, but login appeared successful")
                            return True
                    else:
                        logger.error("Failed to save login cookies")
                        return False
                    
            except requests.RequestException as e:
                logger.warning(f"Login request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
            except Exception as e:
                logger.error(f"Login failed with unexpected error: {e}")
                self.is_logged_in = False
                return False
        
        logger.error(f"Login failed after {max_retries} attempts")
        self.is_logged_in = False
        return False
    
    def fetch_lof_arbitrage_data(self, cnd_status: str = None) -> list[dict]:
        """
        Fetch LOF arbitrage data from jisilu.cn.
        
        Args:
            cnd_status: cnd status code to fetch.
                       Options: LMT (限额), STP (暂停申购), OPN (开放申购), ALL (全部)
                       If None, uses settings.FILTER_CND_STATUS
        
        Returns:
            list[dict]: List of LOF fund data dictionaries.
        """
        logger.info("Fetching LOF arbitrage data...")
        
        if not self.is_logged_in:
            logger.warning("Not logged in, attempting to login...")
            if not self.login():
                logger.error("Failed to login, cannot fetch data")
                return []
        
        # Use configured cnd status if not provided
        if cnd_status is None:
            cnd_status = settings.FILTER_CND_STATUS
        
        try:
            # Fetch from the API endpoint
            data = self._fetch_from_api(cnd=cnd_status)
            if data:
                logger.info(f"Fetched {len(data)} LOF records with cnd={cnd_status}")
                return data
            else:
                logger.warning("API returned no data")
                return []
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data due to network error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch data with unexpected error: {e}")
            return []
    
    def _fetch_from_api(self, cnd: str = 'LMT', show_real: bool = True) -> list[dict]:
        """
        Fetch LOF arbitrage data from the API endpoint.
        
        Args:
            cnd: Subscription status filter code.
                Options: LMT (限额), STP (暂停申购), OPN (开放申购), ALL (全部)
            show_real: If True, fetch real-time estimated value (show_real=y)
        
        Returns:
            list[dict]: List of LOF fund data dictionaries.
        """
        # API endpoint for LOF arbitrage data (found from JavaScript source)
        api_url = settings.JISILU_LOF_ARB_LIST_URL
        
        try:
            # Add timestamp parameter as required by the API
            timestamp = int(time.time() * 1000)
            params = {
                '___jsl': f'LST___t={timestamp}',
                'rp': 50,  # Get more records per page
                'only_holded': '',
                'only_owned': '',
            }
            
            # Add cnd parameter for subscription status filter
            if cnd:
                params['cnd'] = cnd
            
            # Add real-time estimated value flag
            if show_real:
                params['show_real'] = 'y'  # Get real-time estimated value
            
            # Try GET request with timestamp
            response = self.session.get(
                api_url,
                params=params,
                timeout=30
            )
            
            logger.debug(f"API response status: {response.status_code}")
            logger.debug(f"API response content: {response.text[:200]}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for error messages
                if result.get('isError'):
                    logger.warning(f"API returned error: {result.get('msg', 'Unknown error')}")
                    return []
                
                if result.get('rows'):
                    return self._parse_api_response(result)
                    
        except Exception as e:
            logger.debug(f"API fetch failed: {e}")
        
        return []
    
    def _parse_api_response(self, result: dict) -> list[dict]:
        """
        Parse API response into list of dictionaries.
        
        Args:
            result: API response dictionary
            
        Returns:
            list[dict]: Parsed data using original jisilu.cn field names:
                - fund_id: 基金代码
                - fund_nm: 基金名称
                - discount_rt: 溢价率
                - apply_status: 申购状态
                - Other fields from the API
        """
        data = []
        rows = result.get('rows', [])
        
        for row in rows:
            cell = row.get('cell', {})
            if not cell:
                continue
            
            # Parse premium rate (discount_rt) - handle percentage string
            discount_rt = self._parse_float(cell.get('discount_rt'))
            
            fund_data = {
                # Use original jisilu.cn field names
                'fund_id': cell.get('fund_id', ''),
                'fund_nm': cell.get('fund_nm', ''),
                'discount_rt': discount_rt,
                'apply_status': cell.get('apply_status', ''),
                
                # Additional fields for future filtering
                'price': self._parse_float(cell.get('price')),
                'increase_rt': self._parse_float(cell.get('increase_rt')),
                'volume': self._parse_float(cell.get('volume')),
                'fund_nav': self._parse_float(cell.get('fund_nav')),
                'nav_dt': cell.get('nav_dt', ''),
                'estimate_value': self._parse_float(cell.get('estimate_value')),
                'est_val_dt': cell.get('est_val_dt', ''),
                'turnover_rt': self._parse_float(cell.get('turnover_rt')),
                'qdii': cell.get('qdii', ''),
                't0': cell.get('t0', ''),
                'apply_fee': cell.get('apply_fee', ''),
                'redeem_fee': cell.get('redeem_fee', ''),
            }
            data.append(fund_data)
        
        return data
    
    def _parse_float(self, value) -> Optional[float]:
        """Parse string value to float, handling None and empty strings."""
        if value is None or value == '' or value == '-':
            return None
        try:
            return float(str(value).replace('%', ''))
        except (ValueError, TypeError):
            return value
    
    def close(self):
        """Close the session."""
        self.session.close()
        logger.info("Session closed")
    
    def clear_cookies(self):
        """Clear saved cookies from file and session."""
        self.session.cookies.clear()
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
            logger.info(f"Cookie file {self.cookie_file} removed")
