"""
Arbitrage filter module.
Filters LOF funds based on arbitrage criteria.
"""

import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class ArbitrageFilter:
    """Filter for LOF arbitrage opportunities."""
    
    def __init__(
        self,
        premium_threshold: float = None,
        min_volume: float = None,
        blacklist: list = None,
        whitelist: list = None
    ):
        """
        Initialize the filter.
        
        Args:
            premium_threshold: Minimum premium rate (%) to consider. Defaults to settings.FILTER_PREMIUM_THRESHOLD.
            min_volume: Minimum volume (in 10k) to consider. Defaults to settings.FILTER_MIN_VOLUME.
            blacklist: List of fund IDs to exclude. Defaults to settings.FILTER_BLACKLIST.
            whitelist: List of fund IDs to only consider. Defaults to settings.FILTER_WHITELIST.
        """
        self.premium_threshold = premium_threshold if premium_threshold is not None else settings.FILTER_PREMIUM_THRESHOLD
        self.min_volume = min_volume if min_volume is not None else settings.FILTER_MIN_VOLUME
        self.blacklist = blacklist if blacklist is not None else settings.FILTER_BLACKLIST
        self.whitelist = whitelist if whitelist is not None else settings.FILTER_WHITELIST
        
        logger.info(f"ArbitrageFilter initialized with premium_threshold={self.premium_threshold}%, "
                   f"min_volume={self.min_volume}w")
        if self.blacklist:
            logger.info(f"Blacklist: {self.blacklist}")
        if self.whitelist:
            logger.info(f"Whitelist: {self.whitelist}")
    
    def filter(self, lof_data: list[dict]) -> list[dict]:
        """
        Filter LOF data based on arbitrage criteria.
        
        Criteria:
        1. 溢价率 > premium_threshold (premium rate exceeds threshold)
        2. 成交额 >= min_volume (volume meets minimum)
        3. fund_id not in blacklist (not in blacklist)
        4. If whitelist is set, fund_id must be in whitelist
        
        Note: Subscription status filtering is handled by the API via LOF_CND_STATUS parameter.
              The apply_status field is only for display purposes.
        
        Args:
            lof_data: List of LOF fund data dictionaries.
            
        Returns:
            list[dict]: Filtered list of arbitrage opportunities.
        """
        logger.info(f"Filtering {len(lof_data)} LOF records with premium_threshold={self.premium_threshold}%, "
                   f"min_volume={self.min_volume}w")
        
        filtered = []
        for fund in lof_data:
            if self._is_arbitrage_opportunity(fund):
                filtered.append(fund)
        
        logger.info(f"Found {len(filtered)} arbitrage opportunities")
        return filtered
    
    def _is_arbitrage_opportunity(self, fund: dict) -> bool:
        """
        Check if a fund meets arbitrage criteria.
        
        Args:
            fund: LOF fund data dictionary with jisilu.cn field names.
            
        Returns:
            bool: True if fund is an arbitrage opportunity.
        """
        fund_id = fund.get('fund_id', '')
        
        # Check whitelist first (if configured)
        if self.whitelist:
            if fund_id not in self.whitelist:
                return False
        
        # Check blacklist
        if self.blacklist and fund_id in self.blacklist:
            return False
        
        # Check premium rate (discount_rt)
        discount_rt = fund.get('discount_rt')
        if discount_rt is None:
            return False
        
        try:
            discount_rt = float(discount_rt)
        except (ValueError, TypeError):
            return False
        
        if discount_rt <= self.premium_threshold:
            return False
        
        # Check minimum volume (in 10k)
        volume = fund.get('volume')
        if volume is not None:
            try:
                volume = float(volume)
                if volume < self.min_volume:
                    return False
            except (ValueError, TypeError):
                pass
        
        return True
    
