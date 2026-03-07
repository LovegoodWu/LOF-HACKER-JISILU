"""
Email notification module.
Sends email notifications using 126 Mail SMTP server.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Email notification sender using 126 Mail SMTP."""
    
    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        username: str = None,
        password: str = None,
        recipient: str = None
    ):
        """
        Initialize email notifier.
        
        Args:
            smtp_server: SMTP server address. Defaults to settings.EMAIL_SMTP_SERVER.
            smtp_port: SMTP server port. Defaults to settings.EMAIL_SMTP_PORT.
            username: Email username. Defaults to settings.EMAIL_USERNAME.
            password: Email password/auth code. Defaults to settings.EMAIL_PASSWORD.
            recipient: Recipient email address. Defaults to settings.EMAIL_RECIPIENT.
        """
        self.smtp_server = smtp_server or settings.EMAIL_SMTP_SERVER
        self.smtp_port = smtp_port or settings.EMAIL_SMTP_PORT
        self.username = username or settings.EMAIL_USERNAME
        self.password = password or settings.EMAIL_PASSWORD
        self.recipient = recipient or settings.EMAIL_RECIPIENT
        
        logger.info(f"EmailNotifier initialized: {self.smtp_server}:{self.smtp_port}")
    
    def send_arbitrage_alert(
        self,
        opportunities_html: str,
        count: int,
        subject_prefix: str = "LOF 套利机会提醒"
    ) -> bool:
        """
        Send arbitrage opportunity alert email.
        
        Args:
            opportunities_html: HTML table of arbitrage opportunities.
            count: Number of opportunities found.
            subject_prefix: Email subject prefix.
            
        Returns:
            bool: True if email sent successfully, False otherwise.
        """
        # Generate email content
        subject = f"{subject_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        html_content = self._generate_email_html(opportunities_html, count)
        
        return self.send_email(subject, html_content)
    
    def _generate_email_html(self, opportunities_html: str, count: int) -> str:
        """
        Generate full HTML email content.
        
        Args:
            opportunities_html: HTML table of opportunities.
            count: Number of opportunities.
            
        Returns:
            str: Full HTML email content.
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build filter conditions list
        filter_conditions = []
        filter_conditions.append(f"溢价率 > {settings.FILTER_PREMIUM_THRESHOLD}%")
        if settings.FILTER_CND_STATUS:
            # Map cnd code to Chinese description
            cnd_map = {'LMT': '限额', 'STP': '暂停申购', 'OPN': '开放申购', 'ALL': '全部'}
            cnd_description = cnd_map.get(settings.FILTER_CND_STATUS, settings.FILTER_CND_STATUS)
            filter_conditions.append(f"申购状态={cnd_description}")
        if settings.FILTER_MIN_VOLUME > 0:
            filter_conditions.append(f"成交额 > {settings.FILTER_MIN_VOLUME}万")
        if settings.FILTER_BLACKLIST:
            filter_conditions.append(f"黑名单={len(settings.FILTER_BLACKLIST)}只基金")
        if settings.FILTER_WHITELIST:
            filter_conditions.append(f"白名单={len(settings.FILTER_WHITELIST)}只基金")
        
        filter_conditions_str = " | ".join(filter_conditions)
        
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h2 {{ color: #333; }}
                .timestamp {{ color: #666; font-size: 14px; }}
                .summary {{ margin: 20px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; }}
                .filter-conditions {{ color: #666; font-size: 13px; margin-top: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 30px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h2>LOF 套利机会提醒</h2>
            <p class="timestamp">发送时间：{now}</p>
            
            <div class="summary">
                <strong>共发现 {count} 个套利机会</strong>
                <div class="filter-conditions">
                    <strong>筛选条件：</strong>{filter_conditions_str}
                </div>
            </div>
            
            {opportunities_html}
            
            <div class="footer">
                <p>此邮件由 LOF Hacker 自动发送，请勿回复。</p>
                <p>数据来源：集思录 (jisilu.cn)</p>
            </div>
        </body>
        </html>
        """
    
    def send_email(self, subject: str, html_content: str) -> bool:
        """
        Send email with given subject and content.
        
        Args:
            subject: Email subject.
            html_content: HTML email content.
            
        Returns:
            bool: True if email sent successfully, False otherwise.
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = self.recipient
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connect to SMTP server and send
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(0)  # Set to 1 for debug output
                server.login(self.username, self.password)
                server.sendmail(self.username, [self.recipient], msg.as_string())
            
            logger.info(f"Email sent successfully to {self.recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """
        Send a test email to verify configuration.
        
        Returns:
            bool: True if test email sent successfully.
        """
        subject = "LOF Hacker 测试邮件"
        html_content = """
        <html>
        <body>
            <h2>测试邮件</h2>
            <p>如果您收到这封邮件，说明 LOF Hacker 的邮件发送功能配置正确。</p>
            <p>发送时间：{time}</p>
        </body>
        </html>
        """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return self.send_email(subject, html_content)
