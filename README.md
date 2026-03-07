# LOF Hacker - LOF 套利监控器

监控集思录 (jisilu.cn) 网站的 LOF 套利机会，每天定时发送提醒邮件。

## 功能特点

- 🔐 自动登录集思录网站
- 📊 获取 LOF 套利数据
- 🔍 筛选套利机会（申购状态=限额，溢价率>0.5%）
- 📧 每天 13:00 自动发送邮件提醒
- 📝 完整的日志记录

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
# - 集思录账号密码
# - 126 邮箱配置（使用授权码，非登录密码）
# - 邮件接收地址
```

**.env 文件示例：**

```ini
# 集思录账号
JISILU_USERNAME=your_username
JISILU_PASSWORD=your_password

# 126 邮箱配置
EMAIL_SMTP_SERVER=smtp.126.com
EMAIL_SMTP_PORT=465
EMAIL_USERNAME=your_email@126.com
EMAIL_PASSWORD=your_email_auth_code  # 邮箱授权码
EMAIL_RECIPIENT=recipient@example.com

# 套利筛选条件
PREMIUM_THRESHOLD=0.5

# 定时任务时间
SCHEDULE_HOUR=13
SCHEDULE_MINUTE=0
```

### 3. 导入 Cookies（推荐方式）

由于集思录网站有登录速率限制，推荐使用浏览器导出 cookies 的方式登录：

```bash
# 1. 在浏览器中登录 https://www.jisilu.cn/
# 2. 使用浏览器扩展导出 cookies 为 JSON 文件
# 3. 导入 cookies
python tools/import_cookies.py /path/to/cookies.json
```

详细说明请查看 [Cookie 设置指南](docs/COOKIE_SETUP.md)

**注意：** 如果已成功导入 cookies，可以跳过账号密码登录步骤。

### 4. 测试运行

```bash
# 发送测试邮件
python main.py --test

# 立即运行一次监控
python main.py

# 以定时任务模式运行（前台运行）
python main.py --schedule
```

## 部署到阿里云服务器

### 1. 上传代码

```bash
# 使用 scp 或 git 上传代码到服务器
scp -r LOFHacker user@your-server:/path/to/
```

### 2. 安装 Python 环境

```bash
# 安装 Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 创建虚拟环境
cd /path/to/LOFHacker
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 编辑 .env 文件
vim .env
# 填入你的配置信息
```

### 4. 设置定时任务（推荐）

使用 crontab 每天 13:00 执行：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（修改路径为你的实际路径）
0 13 * * * cd /path/to/LOFHacker && /path/to/LOFHacker/.venv/bin/python main.py >> logs/cron.log 2>&1
```

### 5. 验证定时任务

```bash
# 查看 crontab 配置
crontab -l

# 查看 cron 日志
tail -f /var/log/cron.log  # Ubuntu/Debian
# 或
tail -f /var/log/cron      # CentOS/RHEL
```

### 6. 查看应用日志

```bash
# 实时查看日志
tail -f logs/app.log
```

## Cookie 管理
### 导出 Cookies（浏览器端）

1. 安装浏览器扩展：
   - Chrome/Edge: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: [Cookie Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. 登录集思录网站：https://www.jisilu.cn/

3. 点击扩展图标，选择"Export"导出为 JSON 格式

4. 复制 JSON 内容或使用导入工具：
   ```bash
   python tools/import_cookies.py /path/to/cookies.json
   ```

### 清除 Cookies

```bash
# 删除保存的 cookies 文件
rm .jisilu_cookies.pkl
rm .jisilu_cookies.json
```

## 项目结构

```
LOFHacker/
├── .env                    # 环境变量配置（不提交到版本控制）
├── .env.example            # 配置模板
├── requirements.txt        # Python 依赖
├── main.py                 # 主入口
├── README.md               # 说明文档
├── config/
│   ├── __init__.py
│   └── settings.py         # 配置加载模块
├── scraper/
│   ├── __init__.py
│   └── jisilu.py           # 集思录爬虫
├── filter/
│   ├── __init__.py
│   └── arbitrage_filter.py # 套利条件过滤
├── notifier/
│   ├── __init__.py
│   └── email_notifier.py   # 邮件通知模块
├── scheduler/
│   ├── __init__.py
│   └── daily_job.py        # 定时任务调度
├── utils/
│   ├── __init__.py
│   └── logger.py           # 日志配置
└── logs/
    └── app.log             # 运行日志
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--test` | 发送测试邮件 |
| `--schedule` | 以定时任务模式运行（前台） |
| 无参数 | 立即运行一次 |

## 筛选条件

默认筛选条件：
- 申购状态 = "限额"
- 溢价率 > 0.5%

可通过修改 `.env` 文件中的 `PREMIUM_THRESHOLD` 调整溢价率阈值。

## 邮件内容

邮件包含以下信息：
- 基金代码
- 基金名称
- 溢价率
- 申购状态

## 故障排查

### 登录失败

1. 检查 `.env` 中的账号密码是否正确
2. 确认集思录账号状态正常
3. 查看 `logs/app.log` 获取详细错误信息

### 邮件发送失败

1. 126 邮箱需使用**授权码**而非登录密码
2. 获取授权码：登录 126 邮箱 → 设置 → POP3/SMTP/IMAP → 开启 SMTP 服务 → 获取授权码
3. 检查防火墙是否允许 465 端口出站

### 数据获取失败

1. 检查网络连接
2. 确认集思录网站可正常访问
3. 查看日志中的 HTML 响应内容

## 安全建议

1. **不要**将 `.env` 文件提交到版本控制
2. 使用邮箱授权码而非登录密码
3. 定期更新依赖包
4. 在阿里云安全组中限制不必要的出站连接

## 许可证

MIT License

## 免责声明

本工具仅供学习和个人使用，不构成投资建议。使用本工具产生的任何后果由用户自行承担。
