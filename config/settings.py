"""
Configuration module for LOF Arbitrage Monitor.
Loads environment variables from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Jisilu.cn credentials - Cookie file authentication (primary method)
    # Option 1: Cookie file (recommended) - export from browser to .jisilu_cookies.json
    # Option 2: Encrypted username/password (fallback) - configure ENCRYPTED_ credentials below
    
    # Cookie file path
    JISILU_COOKIE_FILE: str = os.getenv("JISILU_COOKIE_FILE", ".jisilu_cookies.json")
    
    # Encrypted credentials (for auto-login without cookie file)
    # Get these values from browser's login request payload
    JISILU_ENCRYPTED_USERNAME: str = os.getenv("JISILU_ENCRYPTED_USERNAME", "")
    JISILU_ENCRYPTED_PASSWORD: str = os.getenv("JISILU_ENCRYPTED_PASSWORD", "")
    
    # Email settings
    EMAIL_SMTP_SERVER: str = os.getenv("EMAIL_SMTP_SERVER", "smtp.126.com")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", "465"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECIPIENT: str = os.getenv("EMAIL_RECIPIENT", "")
    
    # Feishu (Lark) notification settings
    FEISHU_ENABLED: bool = os.getenv("FEISHU_ENABLED", "false").lower() == "true"
    FEISHU_WEBHOOK_URL: str = os.getenv("FEISHU_WEBHOOK_URL", "")
    FEISHU_MESSAGE_TYPE: str = os.getenv("FEISHU_MESSAGE_TYPE", "interactive")
    
    # Feishu message field configuration
    # Required fields (always displayed)
    NOTIFY_REQUIRED_FIELDS: list = os.getenv("NOTIFY_REQUIRED_FIELDS", "code,name,premium_rate,subscription_status").split(",")
    
    # Optional fields (displayed if configured)
    NOTIFY_OPTIONAL_FIELDS: list = os.getenv("NOTIFY_OPTIONAL_FIELDS", "").split(",")
    
    # Arbitrage filter settings (FILTER_ prefix for all filter conditions)
    FILTER_PREMIUM_THRESHOLD: float = float(os.getenv("FILTER_PREMIUM_THRESHOLD", "0.5"))
    FILTER_MIN_VOLUME: float = float(os.getenv("FILTER_MIN_VOLUME", "0"))
    FILTER_CND_STATUS: str = os.getenv("FILTER_CND_STATUS", "LMT")
    
    # Blacklist and whitelist
    FILTER_BLACKLIST: list = [s.strip() for s in os.getenv("FILTER_BLACKLIST", "").replace(",", ",").split(",")] if os.getenv("FILTER_BLACKLIST") else []
    FILTER_WHITELIST: list = [s.strip() for s in os.getenv("FILTER_WHITELIST", "").replace(",", ",").split(",")] if os.getenv("FILTER_WHITELIST") else []
    
    # Schedule settings
    SCHEDULE_HOUR: int = int(os.getenv("SCHEDULE_HOUR", "13"))
    SCHEDULE_MINUTE: int = int(os.getenv("SCHEDULE_MINUTE", "0"))
    
    # URLs
    JISILU_LOGIN_URL: str = "https://www.jisilu.cn/webapi/account/login_process/"
    JISILU_LOF_ARB_LIST_URL: str = "https://www.jisilu.cn/data/lof/arb_list/"
    JISILU_HOME_URL: str = "https://www.jisilu.cn/"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required settings and return list of missing fields."""
        missing = []
        
        # Cookie file is the primary authentication method
        # Username/Password is kept as fallback (has rate limits)
        
        if not cls.EMAIL_USERNAME:
            missing.append("EMAIL_USERNAME")
        if not cls.EMAIL_PASSWORD:
            missing.append("EMAIL_PASSWORD")
        if not cls.EMAIL_RECIPIENT:
            missing.append("EMAIL_RECIPIENT")
        
        return missing


settings = Settings()
