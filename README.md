# LOF Hacker - LOF 套利监控器

监控集思录 (jisilu.cn) 网站的 LOF 套利机会，每天定时发送提醒邮件/飞书通知。

## 功能特点

- 🔐 **自动登录** - 支持 Cookie 文件和加密凭证两种登录方式
- 📊 **数据获取** - 实时获取 LOF 基金套利数据
- 🔍 **智能筛选** - 根据溢价率、申购状态等条件筛选套利机会
- 📧 **邮件通知** - 每天定时发送邮件提醒
- 📱 **飞书通知** - 可选飞书机器人通知
- 📝 **完整日志** - 详细的运行日志记录

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
vim .env
```

**配置说明：**

```ini
# =============================================================================
# 集思录登录配置
# =============================================================================

# 方式 1：Cookie 文件（推荐）
# 从浏览器导出 Cookie 后保存到 data/.jisilu_cookies.json
# 无需配置下面的加密凭证

# 方式 2：加密凭证（备用）
# 从浏览器登录请求中获取加密后的用户名和密码
JISILU_ENCRYPTED_USERNAME=你的加密用户名
JISILU_ENCRYPTED_PASSWORD=你的加密密码

# 获取加密用户名和密码的方法：
# 1. 在浏览器中登录 https://www.jisilu.cn/
# 2. 按 F12 打开开发者工具，切换到 Network 标签
# 3. 重新登录一次，找到 /webapi/account/login_process/ 请求
# 4. 点击该请求，查看"Payload"或"Request"标签
# 5. 复制 user_name 和 password 的值（已经是加密后的）
# 6. 填入 .env 文件的 JISILU_ENCRYPTED_USERNAME 和 JISILU_ENCRYPTED_PASSWORD

# =============================================================================
# 邮件通知配置（126 邮箱）
# =============================================================================
EMAIL_SMTP_SERVER=smtp.126.com
EMAIL_SMTP_PORT=465
EMAIL_USERNAME=your_email@126.com
EMAIL_PASSWORD=your_email_auth_code  # 邮箱授权码，不是登录密码
EMAIL_RECIPIENT=recipient@example.com

# =============================================================================
# 飞书通知配置（可选）
# =============================================================================
FEISHU_ENABLED=false
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_token
FEISHU_MESSAGE_TYPE=text

# =============================================================================
# 套利筛选条件
# =============================================================================
# 溢价率阈值（%）- 只提醒溢价率大于此值的基金
FILTER_PREMIUM_THRESHOLD=0.5

# 最小成交额（万元）- 避免流动性不足
FILTER_MIN_VOLUME=100

# LOF 申购状态 API 参数
# 可选值：LMT (限额), STP (暂停申购), OPN (开放申购), ALL (全部)
FILTER_CND_STATUS=LMT

# =============================================================================
# 定时任务配置
# =============================================================================
# Cron 表达式：分钟 小时 日 月 星期
# 每天 13:00 执行
SCHEDULE_CRON=0 13 * * *
SCHEDULE_TIMEZONE=Asia/Shanghai
```

### 3. 导入 Cookies（推荐方式）

由于集思录网站有登录速率限制，**推荐使用浏览器导出 cookies 的方式登录**，而不是使用账号密码。

#### 方法 A：使用浏览器扩展导出

1. **安装浏览器扩展**：
   - Chrome/Edge: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: [Cookie Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. **登录集思录网站**：https://www.jisilu.cn/

3. **导出 Cookies**：
   - 点击浏览器扩展图标
   - 选择"Export"或"导出"
   - 保存为 JSON 格式文件

4. **导入 Cookies**：
   ```bash
   python tools/import_cookies.py /path/to/cookies.json
   ```

#### 方法 B：使用 Console 代码导出（推荐）

1. 在浏览器中登录 https://www.jisilu.cn/

2. 按 `F12` 打开开发者工具，切换到 **Console** 标签

3. 复制并执行以下代码：
   ```javascript
   copy(JSON.stringify(document.cookie.split('; ').map(c => {
       const [name, value] = c.split('=');
       return {name, value, domain: '.jisilu.cn', path: '/'};
   }), null, 2));
   ```

4. 将复制的 JSON 内容保存为 `data/.jisilu_cookies.json` 文件

#### 方法 C：使用 import_cookies 工具

```bash
# 1. 将导出的 Cookie JSON 文件上传到服务器
scp cookies_export.json user@server:/path/to/

# 2. 在服务器上导入
python tools/import_cookies.py /path/to/cookies_export.json
```

**注意**：如果已成功导入 cookies，可以跳过账号密码登录步骤。

### 4. 配置飞书通知（可选）

除了邮件通知，还可以配置飞书机器人发送提醒：

1. **在飞书群聊中添加机器人**：
   - 打开飞书，进入目标群聊
   - 点击右上角"..." → "添加机器人"
   - 选择"自定义机器人"
   - 设置机器人名称（如"LOF 提醒"）
   - 复制生成的 Webhook 地址

2. **在 .env 文件中配置**：
   ```ini
   FEISHU_ENABLED=true
   FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_token
   FEISHU_MESSAGE_TYPE=text
   ```

详细配置步骤请查看 [飞书通知设置指南](docs/FEISHU_SETUP.md)

**注意**：配置飞书通知后，邮件通知仍然会发送，两者互不影响。

### 5. 测试运行

```bash
# 发送测试邮件
python main.py --test

# 立即运行一次监控
python main.py

# 以定时任务模式运行（前台运行）
python main.py --schedule
```

## 部署到阿里云服务器

详细部署步骤请查看 [阿里云部署指南](docs/ALIYUN_DEPLOYMENT.md)

### 快速部署

```bash
# 1. 上传代码到服务器
scp -r LOFHacker user@your-server:/path/to/

# 2. 在服务器上安装环境
ssh user@your-server
cd /path/to/LOFHacker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
vim .env  # 填入你的配置

# 4. 导入 Cookies（从本地上传）
scp data/.jisilu_cookies.json user@your-server:/path/to/LOFHacker/data/

# 5. 设置 systemd timer（每天 10:00 和 13:00 各执行一次）
# 创建 service 文件
sudo vim /etc/systemd/system/lof-hacker.service
# 内容见下方示例

# 创建 timer 文件
sudo vim /etc/systemd/system/lof-hacker.timer
# 内容见下方示例

# 启用并启动 timer
sudo systemctl daemon-reload
sudo systemctl enable lof-hacker.timer
sudo systemctl start lof-hacker.timer

# 6. 测试运行
python main.py
```

### systemd 配置示例

**1. 创建 service 文件** `/etc/systemd/system/lof-hacker.service`：

```ini
[Unit]
Description=LOF Hacker Arbitrage Monitor
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/LOF-HACKER-JISILU
ExecStart=/root/LOF-HACKER-JISILU/.venv/bin/python /root/LOF-HACKER-JISILU/main.py
StandardOutput=journal
StandardError=journal
```

**2. 创建 timer 文件** `/etc/systemd/system/lof-hacker.timer`：

```ini
[Unit]
Description=Run LOF Hacker daily at 10:00 and 13:00
Requires=lof-hacker.service

[Timer]
# 每天 10:00 触发
OnCalendar=*-*-* 10:00:00
# 每天 13:00 触发（多行写法）
OnCalendar=*-*-* 13:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**3. 常用命令**：

```bash
# 查看所有激活的 timer
systemctl list-timers

# 查看 timer 状态
systemctl status lof-hacker.timer

# 查看 timer 详细信息（包括下次触发时间）
systemctl list-timers lof-hacker.timer --all

# 查看日志
journalctl -u lof-hacker.service
journalctl -fu lof-hacker.service  # 实时跟踪
```

## 项目结构

```
LOFHacker/
├── data/                           # 数据目录（Cookie 文件存放处）
│   ├── .jisilu_cookies.json        # 主 Cookie 文件（不提交到 Git）
│   └── .jisilu_cookies_test.json   # 测试 Cookie 文件（不提交到 Git）
├── .env                            # 环境变量配置（不提交到 Git）
├── .env.example                    # 配置模板
├── .gitignore                      # Git 忽略文件配置
├── requirements.txt                # Python 依赖
├── main.py                         # 主入口
├── README.md                       # 说明文档
├── config/
│   └── settings.py                 # 配置加载模块
├── scraper/
│   └── jisilu.py                   # 集思录爬虫
├── filter/
│   └── arbitrage_filter.py         # 套利条件过滤
├── notifier/
│   ├── email_notifier.py           # 邮件通知模块
│   └── feishu_notifier.py          # 飞书通知模块
├── scheduler/
│   └── daily_job.py                # 定时任务调度
├── utils/
│   └── logger.py                   # 日志配置
├── tools/
│   ├── import_cookies.py           # Cookie 导入工具
│   └── test_login.py               # 登录测试工具
└── docs/
    ├── ALIYUN_DEPLOYMENT.md        # 阿里云部署指南
    ├── COOKIE_SETUP.md             # Cookie 设置指南
    ├── FEISHU_SETUP.md             # 飞书通知设置
    └── SECURITY.md                 # 安全建议
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--test` | 发送测试邮件 |
| `--schedule` | 以定时任务模式运行（前台） |
| 无参数 | 立即运行一次 |

## 筛选条件

默认筛选条件：
- 申购状态 = "限额"（`FILTER_CND_STATUS=LMT`）
- 溢价率 > 0.5%（`FILTER_PREMIUM_THRESHOLD=0.5`）
- 最小成交额 > 100 万元（`FILTER_MIN_VOLUME=100`）

可通过修改 `.env` 文件调整筛选条件。

## 通知内容

### 邮件通知

邮件包含以下信息：
- 基金代码
- 基金名称
- 溢价率
- 申购状态

### 飞书通知

飞书消息支持两种格式：
- `text` - 纯文本消息
- `interactive` - 交互式卡片消息（需要企业验证）

## 故障排查

### 📱 飞书通知配置

**如何获取飞书 Webhook URL？**

1. 打开飞书，进入目标群聊
2. 点击右上角"..." → "添加机器人"
3. 选择"自定义机器人"
4. 设置机器人名称（如"LOF 提醒"）
5. 复制生成的 Webhook 地址
6. 填入 `.env` 文件的 `FEISHU_WEBHOOK_URL` 配置项

详细步骤请查看 [飞书通知设置指南](docs/FEISHU_SETUP.md)

### 登录失败

**症状**：日志显示"Login failed"或"cookies expired"

**解决方案**：
1. 检查 `.env` 中的加密凭证是否正确
2. 确认集思录账号状态正常
3. 查看 `logs/app.log` 获取详细错误信息
4. 重新从浏览器导出 Cookie 并导入

**获取加密凭证方法**：
1. 在浏览器中登录集思录
2. 按 F12 打开开发者工具 → Network 标签
3. 重新登录一次，找到 `login_process` 请求
4. 查看请求的 Payload/Request 参数
5. 复制 `user_name` 和 `password` 的值（已加密）

### 邮件发送失败

**症状**：日志显示"SMTP Authentication Error"

**解决方案**：
1. 确认使用的是**授权码**而非登录密码
2. 检查 126 邮箱是否开启了 SMTP 服务
3. 验证安全组是否允许 465 端口出站

**获取授权码步骤**：
1. 登录 126 邮箱网页版
2. 点击"设置" → "POP3/SMTP/IMAP"
3. 开启"SMTP 服务"
4. 点击"生成授权码"
5. 按短信验证获取授权码

### 数据获取失败

**症状**：日志显示"Failed to fetch data"或"API returned no data"

**解决方案**：
1. 检查网络连接
2. 确认集思录网站可正常访问
3. 查看日志中的响应内容
4. 确认 Cookie 文件未过期

### Cookie 过期

**症状**：日志显示"cookies expired"或"login may have expired"

**解决方案**：
```bash
# 1. 在浏览器重新登录并导出 Cookie
# 2. 上传新的 Cookie 文件
scp data/.jisilu_cookies.json user@server:/path/to/LOFHacker/data/

# 3. 或者使用加密凭证自动登录（无需 Cookie）
vim .env
# 填写 JISILU_ENCRYPTED_USERNAME 和 JISILU_ENCRYPTED_PASSWORD
```

### systemd Timer 不执行

**症状**：timer 已启用但到时间不执行

**解决方案**：
```bash
# 1. 检查 timer 状态
systemctl status lof-hacker.timer
systemctl list-timers lof-hacker.timer --all

# 2. 检查 service 状态
systemctl status lof-hacker.service

# 3. 查看日志
journalctl -u lof-hacker.service --since today

# 4. 如果配置有修改，重新加载
sudo systemctl daemon-reload
sudo systemctl restart lof-hacker.timer

# 5. 手动触发一次测试
sudo systemctl start lof-hacker.service
```

**常见问题**：
- `OnCalendar` 语法错误：确保每个时间单独一行
- `Timezone` 配置：systemd 使用系统时区，不要配置 Timezone
- 权限问题：确保 `WorkingDirectory` 和 `ExecStart` 路径正确

## 相关文档

- [Cookie 设置指南](docs/COOKIE_SETUP.md) - 浏览器导出 Cookie 详细步骤
- [飞书通知设置](docs/FEISHU_SETUP.md) - 配置飞书机器人通知
- [阿里云部署指南](docs/ALIYUN_DEPLOYMENT.md) - 服务器部署完整教程
- [加密登录设置](docs/ENCRYPTED_LOGIN_SETUP.md) - 使用加密凭证自动登录
- [安全建议](docs/SECURITY.md) - 安全配置最佳实践

## 安全建议

1. **不要**将 `.env` 文件提交到版本控制
2. 使用邮箱授权码而非登录密码
3. 定期更新依赖包
4. 在阿里云安全组中限制不必要的出站连接
5. 使用 SSH 密钥登录服务器
6. 定期更新 Cookie 文件

## 成本估算

部署到阿里云服务器的成本估算：

| 项目 | 配置 | 价格（月） |
|------|------|-----------|
| ECS 实例 | 突发性能型 t6, 2 核 2G | ¥60-80 |
| 带宽 | 按量付费 1Mbps | ¥20-30 |
| 系统盘 | 40GB 高效云盘 | ¥10 |
| **总计** | | **¥90-120/月** |

> 注：价格仅供参考，实际价格以阿里云官网为准。新用户通常有优惠活动。

## 许可证

MIT License

## 免责声明

本工具仅供学习和个人使用，不构成投资建议。使用本工具产生的任何后果由用户自行承担。
