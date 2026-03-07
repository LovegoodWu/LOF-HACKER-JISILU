#!/usr/bin/env python3
"""
测试集思录登录功能，打印登录后获取的 Cookie。

使用方法：
1. 确保 .env 文件中已配置 JISILU_ENCRYPTED_USERNAME 和 JISILU_ENCRYPTED_PASSWORD
2. 运行：python tools/test_login.py

注意：测试登录的 Cookie 会保存到 .jisilu_cookies_test.json 文件，不会影响主程序的 Cookie 文件。
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.jisilu import JisiluScraper
import logging
import json

# Test cookie file path
TEST_COOKIE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '.jisilu_cookies_test.json')

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test login and print cookies."""
    print("=" * 60)
    print("集思录登录测试工具")
    print("=" * 60)
    print()
    
    # Create scraper instance
    scraper = JisiluScraper()
    
    # Check if encrypted credentials are configured
    from config.settings import settings
    
    if not settings.JISILU_ENCRYPTED_USERNAME:
        print("❌ 错误：JISILU_ENCRYPTED_USERNAME 未配置")
        print()
        print("请在 .env 文件中配置：")
        print("  JISILU_ENCRYPTED_USERNAME=你的加密用户名")
        print("  JISILU_ENCRYPTED_PASSWORD=你的加密密码")
        print()
        print("获取加密值的方法：")
        print("  1. 浏览器访问 https://www.jisilu.cn")
        print("  2. F12 打开开发者工具 → Network 标签")
        print("  3. 执行登录操作")
        print("  4. 找到 login_process 请求")
        print("  5. 复制请求参数中的 user_name 和 password 值")
        return 1
    
    if not settings.JISILU_ENCRYPTED_PASSWORD:
        print("❌ 错误：JISILU_ENCRYPTED_PASSWORD 未配置")
        return 1
    
    print("✅ 配置检查通过")
    print()
    print(f"加密用户名：{settings.JISILU_ENCRYPTED_USERNAME[:8]}...{settings.JISILU_ENCRYPTED_USERNAME[-8:]}")
    print(f"加密密码：{settings.JISILU_ENCRYPTED_PASSWORD[:8]}...{settings.JISILU_ENCRYPTED_PASSWORD[-8:]}")
    print()
    
    # Attempt login
    print("-" * 60)
    print("开始登录...")
    print("-" * 60)
    
    success = scraper.login()
    
    print()
    print("-" * 60)
    print("登录结果")
    print("-" * 60)
    
    if success:
        print("✅ 登录成功！")
        print()
        
        # Print cookies
        print("获取到的 Cookie：")
        print("-" * 60)
        try:
            cookies = dict(scraper.session.cookies)
            for name, value in cookies.items():
                if len(value) > 60:
                    # Truncate long values
                    value_display = f"{value[:30]}...{value[-30:]}"
                else:
                    value_display = value
                print(f"  {name}: {value_display}")
            print()
            
            # Print cookie summary
            print(f"Cookie 总数：{len(cookies)}")
        except Exception as e:
            # Handle duplicate cookie names
            print(f"⚠️  注意：存在同名 Cookie，无法转换为字典：{e}")
            print()
            # Print raw cookies instead
            for cookie in scraper.session.cookies:
                value = cookie.value
                if len(value) > 60:
                    value_display = f"{value[:30]}...{value[-30:]}"
                else:
                    value_display = value
                print(f"  {cookie.name}: {value_display} (domain: {cookie.domain})")
            print()
            print(f"Cookie 总数：{len(list(scraper.session.cookies))}")
        
        # Check for important cookies
        important_cookies = ['kbzw__Session', 'kbzw__user_login']
        print()
        print("关键 Cookie 检查：")
        cookie_names = [c.name for c in scraper.session.cookies]
        for key in important_cookies:
            if key in cookie_names:
                print(f"  ✅ {key}: 存在")
            else:
                print(f"  ⚠️  {key}: 不存在")
        
        # Save cookies to test file
        print()
        print("-" * 60)
        print("保存 Cookie 到测试文件...")
        print("-" * 60)
        
        # Save to test cookie file
        cookies_data = {
            'cookies': [
                {
                    'name': c.name,
                    'value': c.value,
                    'domain': c.domain,
                    'path': c.path,
                    'secure': c.secure,
                    'expires': c.expires
                }
                for c in scraper.session.cookies
            ],
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        try:
            with open(TEST_COOKIE_FILE, 'w') as f:
                json.dump(cookies_data, f, indent=2)
            print(f"✅ Cookie 已保存到测试文件：{TEST_COOKIE_FILE}")
            print(f"   (主程序 Cookie 文件未受影响：{settings.JISILU_COOKIE_FILE})")
        except Exception as e:
            print(f"❌ 保存 Cookie 失败：{e}")
        
        print()
        print("=" * 60)
        print("测试完成！")
        print("=" * 60)
        return 0
    else:
        print("❌ 登录失败！")
        print()
        print("可能的原因：")
        print("  1. 加密凭证已过期，请重新获取")
        print("  2. 用户名或密码错误")
        print("  3. 网络连接问题")
        print()
        print("建议：")
        print("  1. 重新从浏览器获取加密凭证")
        print("  2. 检查 .env 文件配置是否正确")
        print("  3. 查看上方日志输出获取详细错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
