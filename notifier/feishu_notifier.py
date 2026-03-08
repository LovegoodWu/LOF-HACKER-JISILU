"""
Feishu (Lark) notification module.
Sends notifications via Feishu webhook bot.
"""

import logging
import requests
from datetime import datetime
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class FeishuNotifier:
    """Feishu notification sender via webhook."""
    
    def __init__(
        self,
        webhook_url: str = None,
        message_type: str = None
    ):
        """
        Initialize Feishu notifier.
        
        Args:
            webhook_url: Feishu webhook URL. Defaults to settings.FEISHU_WEBHOOK_URL.
            message_type: Message type ('text' or 'interactive'). Defaults to settings.FEISHU_MESSAGE_TYPE.
        """
        self.webhook_url = webhook_url or settings.FEISHU_WEBHOOK_URL
        self.message_type = message_type or settings.FEISHU_MESSAGE_TYPE
        
        logger.info(f"FeishuNotifier initialized: message_type={self.message_type}")
    
    def send_arbitrage_alert(
        self,
        opportunities: list[dict],
        count: int,
        title: str = "LOF 套利机会提醒"
    ) -> bool:
        """
        Send arbitrage opportunity alert to Feishu.
        
        Args:
            opportunities: List of arbitrage opportunity data.
            count: Number of opportunities found.
            title: Message title.
            
        Returns:
            bool: True if notification sent successfully, False otherwise.
        """
        if self.message_type == "interactive":
            return self._send_interactive_message(opportunities, count, title)
        else:
            return self._send_text_message(opportunities, count, title)
    
    def _send_text_message(
        self,
        opportunities: list[dict],
        count: int,
        title: str
    ) -> bool:
        """
        Send text format message.
        
        Args:
            opportunities: List of opportunity data.
            count: Number of opportunities.
            title: Message title.
            
        Returns:
            bool: True if sent successfully.
        """
        try:
            # Build filter conditions string
            filter_conditions = []
            filter_conditions.append(f"溢价率>{settings.FILTER_PREMIUM_THRESHOLD}%")
            if settings.FILTER_CND_STATUS:
                # Map cnd code to Chinese description
                cnd_map = {'LMT': '限额', 'STP': '暂停申购', 'OPN': '开放申购', 'ALL': '全部'}
                cnd_description = cnd_map.get(settings.FILTER_CND_STATUS, settings.FILTER_CND_STATUS)
                filter_conditions.append(f"申购状态={cnd_description}")
            if settings.FILTER_MIN_VOLUME > 0:
                filter_conditions.append(f"成交额>{settings.FILTER_MIN_VOLUME} 万")
            
            # Build text content
            text_lines = [f"【{title}】\n"]
            text_lines.append(f"⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            text_lines.append(f"📊 共发现 {count} 个套利机会\n")
            text_lines.append(f"筛选条件：{' | '.join(filter_conditions)}\n")
            
            # Add top 5 opportunities
            for i, opp in enumerate(opportunities[:5], 1):
                code = opp.get('fund_id', '')
                name = opp.get('fund_nm', '')
                premium = opp.get('discount_rt', '')
                status = opp.get('apply_status', '')
                
                text_lines.append(f"{i}. {code} {name}")
                text_lines.append(f"   溢价率：{premium}% | 状态：{status}\n")
            
            if len(opportunities) > 5:
                text_lines.append(f"\n... 还有 {len(opportunities) - 5} 个机会，请查看完整列表")
            
            text_content = "\n".join(text_lines)
            
            # Build message payload (Feishu text format)
            payload = {
                "msg_type": "text",
                "content": {
                    "text": text_content
                }
            }
            
            logger.debug(f"Text message content: {text_content[:200]}...")
            
            return self._send_request(payload)
            
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            return False
    
    def _send_interactive_message(
        self,
        opportunities: list[dict],
        count: int,
        title: str
    ) -> bool:
        """
        Send interactive card message (rich format).
        
        Args:
            opportunities: List of opportunity data.
            count: Number of opportunities.
            title: Message title.
            
        Returns:
            bool: True if sent successfully.
        """
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Build filter conditions string
            filter_conditions = []
            filter_conditions.append(f"溢价率 > {settings.FILTER_PREMIUM_THRESHOLD}%")
            if settings.FILTER_CND_STATUS:
                # Map cnd code to Chinese description
                cnd_map = {'LMT': '限额', 'STP': '暂停申购', 'OPN': '开放申购', 'ALL': '全部'}
                cnd_description = cnd_map.get(settings.FILTER_CND_STATUS, settings.FILTER_CND_STATUS)
                filter_conditions.append(f"申购状态={cnd_description}")
            if settings.FILTER_MIN_VOLUME > 0:
                filter_conditions.append(f"成交额>{settings.FILTER_MIN_VOLUME} 万")
            if settings.FILTER_BLACKLIST:
                filter_conditions.append(f"黑名单={len(settings.FILTER_BLACKLIST)}只基金")
            if settings.FILTER_WHITELIST:
                filter_conditions.append(f"白名单={len(settings.FILTER_WHITELIST)}只基金")
            
            # Build message payload using Feishu's interactive card format
            # Reference: https://open.feishu.cn/document/ukTMzUjL4YDM00i2NATN/post_message/interactive-card/how-to-use-interative-cards
            # For custom bots, use markdown with simple list format for best compatibility
            
            # Build the full card content as a single markdown block
            card_content = []
            card_content.append(f"**⏰ 时间：** {now}")
            card_content.append(f"**📊 数量：** 共发现 {count} 个套利机会")
            card_content.append(f"**筛选条件：** {' | '.join(filter_conditions)}")
            card_content.append("")
            
            # Opportunity list with clean formatted layout
            if opportunities:
                card_content.append("**📈 套利机会列表：**")
                card_content.append("")
                
                # Direct mapping from jisilu API field names to Chinese display names
                field_display_names = {
                    'fund_id': '代码',
                    'fund_nm': '名称',
                    'discount_rt': '溢价率',
                    'apply_status': '申购状态',
                    'price': '现价',
                    'estimate_value': '估值',
                    'fund_nav': '净值',
                    'nav_dt': '净值日期',
                    'volume': '成交额',
                    'turnover_rt': '换手率'
                }
                
                for i, opp in enumerate(opportunities[:10], 1):
                    row_parts = []
                    
                    # Add required fields
                    for field in settings.NOTIFY_REQUIRED_FIELDS:
                        field = field.strip()
                        if field not in field_display_names:
                            continue
                        
                        value = opp.get(field, '')
                        
                        # Format value based on field type
                        if field == 'discount_rt':
                            if isinstance(value, (int, float)):
                                value = f"{value:.2f}"
                            row_parts.append(f"溢价率：**{value}%**")
                        elif field == 'fund_id':
                            row_parts.append(f"**{i:2}. {value}**")
                        else:
                            if isinstance(value, float):
                                value = f"{value:.3f}"
                            row_parts.append(str(value))
                    
                    # Add optional fields
                    for field in settings.NOTIFY_OPTIONAL_FIELDS:
                        field = field.strip()
                        if field not in field_display_names:
                            continue
                        
                        value = opp.get(field, '')
                        
                        # Format value based on field type
                        if isinstance(value, float):
                            value = f"{value:.3f}"
                        
                        # Special handling for estimate_value - show italic for real-time
                        if field == 'estimate_value':
                            display_name = field_display_names.get(field, field)
                            # Check if it's real-time estimated value (rt_eval == 1)
                            if opp.get('rt_eval') == 1:
                                # Use italic markdown syntax: _text_
                                row_parts.append(f"_{display_name}: {value} (实时)_")
                            else:
                                row_parts.append(f"{display_name}: {value}")
                        else:
                            display_name = field_display_names.get(field, field)
                            row_parts.append(f"{display_name}: {value}")
                    
                    # Join all parts with separator
                    card_content.append("  |  ".join(row_parts))
                
                if len(opportunities) > 10:
                    card_content.append("")
                    card_content.append(f"> 💡 还有 {len(opportunities) - 10} 个机会，请打开集思录查看更多")
            else:
                card_content.append("")
                card_content.append("💡 暂无符合条件的套利机会")
            
            card_content.append("")
            card_content.append("---")
            card_content.append(f"📊 数据来源：集思录 (jisilu.cn)")
            
            # Use the simplified card format with a single content element
            payload = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "content": title,
                            "tag": "plain_text"
                        },
                        "template": "blue"
                    },
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": "\n".join(card_content)
                        }
                    ]
                }
            }
            
            logger.debug(f"Interactive card payload: {payload}")
            
            return self._send_request(payload)
            
        except Exception as e:
            logger.error(f"Failed to send interactive message: {e}")
            return False
    
    def _send_request(self, payload: dict) -> bool:
        """
        Send HTTP request to Feishu webhook.
        
        Args:
            payload: Message payload.
            
        Returns:
            bool: True if sent successfully.
        """
        try:
            # Mask webhook URL for security
            masked_url = self.webhook_url[:30] + "..." if len(self.webhook_url) > 30 else self.webhook_url
            logger.info(f"Sending Feishu notification to {masked_url}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            
            result = response.json()
            
            # Feishu returns {"code": 0, "msg": "success"} on success
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                logger.info("Feishu notification sent successfully")
                return True
            else:
                logger.error(f"Feishu API error: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending Feishu notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Feishu notification: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """
        Send a test message to verify configuration.
        
        Returns:
            bool: True if test message sent successfully.
        """
        if self.message_type == "interactive":
            return self._send_interactive_message(
                opportunities=[
                    {
                        'fund_id': '161128',
                        'fund_nm': '华宝油气',
                        'discount_rt': '1.25',
                        'apply_status': '限额'
                    }
                ],
                count=1,
                title="LOF Hacker 测试消息"
            )
        else:
            return self._send_text_message(
                opportunities=[
                    {
                        'fund_id': '161128',
                        'fund_nm': '华宝油气',
                        'discount_rt': '1.25',
                        'apply_status': '限额'
                    }
                ],
                count=1,
                title="LOF Hacker 测试消息"
            )
