#!/usr/bin/env python3
"""
从浏览器手动复制 Cookie 并测试登录的工具。

使用方法（两种方式）：

方式一：直接粘贴 Cookie 字符串
1. 在浏览器中登录 https://www.jisilu.cn/
2. 打开开发者工具（F12）→ Console
3. 运行：copy(document.cookie)
4. 复制剪贴板内容
5. 运行：python tools/test_cookies.py --cookie "粘贴的内容"

方式二：粘贴 JSON 格式
1. 在浏览器中登录 https://www.jisilu.cn/
2. 打开开发者工具（F12）→ Console
3. 运行：copy(JSON.stringify(document.cookie.split('; ').map(c => {
       const [name, value] = c.split('=');
       return {name, value};
   }), null, 2));
4. 复制剪贴板内容
5. 运行：python tools/test_cookies.py --json "粘贴的内容"
"""

import json
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time


def parse_cookie_string(cookie_str: str) -> dict:
    """Parse cookie string from browser (document.cookie format)."""
    cookies = {}
    for part in cookie_str.split(';'):
        if '=' in part:
            name, value = part.split('=', 1)
            name = name.strip()
            value = value.strip()
            if name and value:
                cookies[name] = value
    return cookies


def parse_cookie_json(cookie_json: str) -> dict:
    """Parse cookie JSON from browser console output."""
    try:
        cookies_data = json.loads(cookie_json)
        cookies = {}
        for item in cookies_data:
            if isinstance(item, dict) and 'name' in item and 'value' in item:
                cookies[item['name']] = item['value']
        return cookies
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        return {}


def test_cookies(cookies: dict, save: bool = True) -> bool:
    """Test if cookies are valid for accessing LOF arbitrage data."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.jisilu.cn/data/lof/',
        'X-Requested-With': 'XMLHttpRequest',
    })
    
    # Set all cookies
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.jisilu.cn', path='/')
    
    print(f"设置 Cookies: {list(cookies.keys())}")
    print()
    
    # Test API access
    timestamp = int(time.time() * 1000)
    api_url = 'https://www.jisilu.cn/data/lof/arb_list/'
    params = {
        '___jsl': f'LST___t={timestamp}',
        'rp': 5,
    }
    
    print('访问套利列表 API...')
    response = session.get(api_url, params=params, timeout=30)
    
    try:
        result = response.json()
        if result.get('isError'):
            msg = result.get('msg', 'Unknown error')
            # Truncate HTML tags
            import re
            msg = re.sub(r'<[^>]+>', '', msg)[:100]
            print(f'❌ 错误：{msg}')
            return False
        elif result.get('rows'):
            print(f'✅ 成功！获取到 {len(result.get("rows", []))} 条数据')
            print()
            print('前 5 条数据:')
            for row in result.get('rows', [])[:5]:
                cell = row.get('cell', {})
                fund_id = cell.get('fund_id', 'N/A')
                fund_nm = cell.get('fund_nm', 'N/A')
                premium_rt = cell.get('premium_rt', 'N/A')
                apply_status = cell.get('apply_status', 'N/A')
                print(f'  代码：{fund_id}, 名称：{fund_nm}, 溢价率：{premium_rt}%, 申购状态：{apply_status}')
            return True
        else:
            print(f'⚠️ 未获取到数据')
            return False
    except Exception as e:
        print(f'解析失败：{e}')
        print(f'响应内容：{response.text[:300]}')
        return False


def main():
    parser = argparse.ArgumentParser(description='从浏览器导入 Cookies 并测试')
    parser.add_argument('--cookie', '-c', type=str, help='浏览器 document.cookie 输出的字符串')
    parser.add_argument('--json', '-j', type=str, help='浏览器 JSON 格式输出的 cookies')
    parser.add_argument('--file', '-f', type=str, help='从文件读取 cookies（JSON 格式）')
    parser.add_argument('--no-save', action='store_true', help='不保存 cookies 到文件')
    
    args = parser.parse_args()
    
    cookies = {}
    
    if args.file:
        # Read from file
        if not os.path.exists(args.file):
            print(f"文件不存在：{args.file}")
            return 1
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
            cookies = parse_cookie_json(content)
            if not cookies:
                cookies = parse_cookie_string(content)
        print(f"从文件读取 cookies: {args.file}")
    
    elif args.json:
        # Parse JSON format
        cookies = parse_cookie_json(args.json)
        print("解析 JSON 格式 cookies")
    
    elif args.cookie:
        # Parse cookie string format
        cookies = parse_cookie_string(args.cookie)
        print("解析 Cookie 字符串格式")
    
    else:
        # Interactive mode - ask user to paste
        print("=" * 60)
        print("从浏览器导入 Cookies")
        print("=" * 60)
        print()
        print("请按照以下步骤操作：")
        print()
        print("方式一（推荐）- Cookie 字符串：")
        print("1. 在浏览器中登录 https://www.jisilu.cn/")
        print("2. 打开开发者工具（F12）→ Console")
        print("3. 运行：copy(document.cookie)")
        print("4. 复制剪贴板内容")
        print("5. 运行：python tools/test_cookies.py --cookie \"粘贴的内容\"")
        print()
        print("方式二 - JSON 格式：")
        print("1. 在浏览器中登录 https://www.jisilu.cn/")
        print("2. 打开开发者工具（F12）→ Console")
        print("3. 运行以下代码：")
        print("   copy(JSON.stringify(document.cookie.split('; ').map(c => {")
        print("       const [name, value] = c.split('=');")
        print("       return {name, value};")
        print("   }), null, 2));")
        print("4. 复制剪贴板内容")
        print("5. 运行：python tools/test_cookies.py --json \"粘贴的内容\"")
        print()
        print("=" * 60)
        print()
        print("请输入 cookie 字符串（直接粘贴 document.cookie 的输出）：")
        
        cookie_str = input().strip()
        if cookie_str:
            cookies = parse_cookie_string(cookie_str)
        else:
            print("未输入内容，退出")
            return 1
    
    if not cookies:
        print("❌ 未解析到任何 cookies")
        return 1
    
    print(f"\n解析到 {len(cookies)} 个 cookies: {list(cookies.keys())}")
    print()
    
    # Test cookies
    if test_cookies(cookies, save=not args.no_save):
        print()
        print("✅ Cookies 有效！保存到文件...")
        
        # Save cookies to file
        cookie_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.jisilu_cookies.json')
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump([{'name': k, 'value': v, 'domain': '.jisilu.cn', 'path': '/'} for k, v in cookies.items()], f, indent=2)
        print(f"Cookies 已保存到：{cookie_file}")
        print()
        print("现在可以运行：python main.py 来获取 LOF 套利数据")
        return 0
    else:
        print()
        print("❌ Cookies 无效，请检查：")
        print("  1. 是否已登录集思录网站")
        print("  2. cookies 是否已过期（请刷新页面重新复制）")
        print("  3. 是否有 LOF 套利数据的会员权限")
        return 1


if __name__ == "__main__":
    sys.exit(main())
