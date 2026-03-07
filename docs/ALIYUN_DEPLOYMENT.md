# 阿里云部署指南

本指南详细介绍如何将 LOF Hacker 部署到阿里云服务器，并设置每天定时执行。

## 目录

1. [准备工作](#1-准备工作)
2. [步骤 1：购买和配置阿里云服务器](#2-步骤 1 购买和配置阿里云服务器)
3. [步骤 2：上传代码到服务器](#3-步骤 2 上传代码到服务器)
4. [步骤 3：安装 Python 环境](#4-步骤 3 安装 python 环境)
5. [步骤 4：配置应用](#5-步骤 4 配置应用)
6. [步骤 5：设置定时任务](#6-步骤 5 设置定时任务)
7. [步骤 6：验证和监控](#7-步骤 6 验证和监控)
8. [常见问题](#8-常见问题)

---

## 1. 准备工作

### 1.1 阿里云账号
- 注册 [阿里云账号](https://www.aliyun.com/)
- 完成实名认证

### 1.2 创建 AccessKey（可选，用于 API 调用）
1. 登录阿里云控制台
2. 点击右上角头像 → "AccessKey 管理"
3. 创建 AccessKey（建议使用 RAM 用户）

### 1.3 准备配置信息
在部署前，请准备好以下信息：
- 集思录 Cookie 文件（从浏览器导出）
- 邮箱配置（SMTP 服务器、授权码）
- 飞书 Webhook URL（可选）

---

## 2. 步骤 1：购买和配置阿里云服务器

### 2.1 购买 ECS 实例
1. 登录 [阿里云 ECS 控制台](https://ecs.console.aliyun.com/)
2. 点击"创建实例"
3. 选择配置

### 2.2 配置安全组
1. 在实例详情页点击"安全组"
2. 添加以下规则：
   - **入方向**：
     - TCP 22（SSH 连接）
   - **出方向**：
     - TCP 443（HTTPS，访问集思录网站）
     - TCP 465（SMTPS，发送邮件）

---

## 3. 步骤 2：上传代码到服务器

### 方法 A：使用 Git（推荐）

```bash
# 1. 在本地提交代码到 Git 仓库
cd /your-path-to-project/LOF-HACKER-JISILU
git add .
git commit -m "Initial commit"

# 2. 创建远程仓库（GitHub/Gitee/阿里云 Codeup）
# 以 GitHub 为例，创建仓库后执行：
git remote add origin git@github.com:your-username/LOF-HACKER-JISILU.git
git push -u origin main

# 3. 在服务器上克隆代码
ssh root@your-server-ip
git clone git@github.com:your-username/LOF-HACKER-JISILU.git
cd LOF-HACKER-JISILU
```

### 方法 B：使用 SCP 上传

```bash
# 在本地执行，上传整个项目
scp -r /your-path-to-project/LOF-HACKER-JISILU root@your-server-ip:/root/

# 或者使用 rsync（支持断点续传）
rsync -avz /your-path-to-project/LOF-HACKER-JISILU/ root@your-server-ip:/root/LOF-HACKER-JISILU/
```

---

## 4. 步骤 3：安装 Python 环境

### Ubuntu/Debian 系统

```bash
# 1. 更新软件源
sudo apt update

# 2. 安装 Python 3 和 pip
sudo apt install -y python3 python3-pip python3-venv

# 3. 验证安装
python3 --version  # 应显示 Python 3.8+
pip3 --version
```

### CentOS/RHEL 系统

```bash
# 1. 安装 EPEL 源
sudo yum install -y epel-release

# 2. 安装 Python 3
sudo yum install -y python3 python3-pip

# 3. 验证安装
python3 --version
pip3 --version
```

### 创建虚拟环境

```bash
cd /root/LOF-HACKER-JISILU

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 验证安装
pip list
```

---

## 5. 步骤 4：配置应用

### 5.1 创建 .env 配置文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

### 5.2 填写配置

### 5.3 上传 Cookie 文件（推荐方式）

**方法 A：本地导出后上传**

```bash
# 1. 在浏览器中登录 https://www.jisilu.cn/
# 2. 使用扩展导出 Cookie 为 JSON 文件
# 3. 上传到服务器

scp data/.jisilu_cookies.json root@your-server-ip:/root/LOF-HACKER-JISILU/data/
```

**方法 B：使用 import_cookies 工具**

```bash
# 1. 将导出的 Cookie JSON 文件上传到服务器
scp cookies_export.json root@your-server-ip:/root/

# 2. 在服务器上导入
ssh root@your-server-ip
cd /root/LOF-HACKER-JISILU
source .venv/bin/activate
python tools/import_cookies.py /root/cookies_export.json
```

### 5.4 创建日志目录

```bash
mkdir -p logs
touch logs/app.log
chmod 644 logs/app.log
```

### 5.5 测试运行

```bash
# 测试运行一次
python main.py

# 查看日志
tail -f logs/app.log
```

---

## 6. 步骤 5：设置定时任务
### 使用 systemd Timer（更现代的方式）

**1. 创建服务文件**

```bash
sudo vim /etc/systemd/system/lof-hacker.service
```

```ini
[Unit]
Description=LOF Hacker Arbitrage Monitor
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/path-to-your-project/LOF-HACKER-JISILU
ExecStart=/path-to-your-project/LOF-HACKER-JISILU/.venv/bin/python /path-to-your-project/LOF-HACKER-JISILU/main.py
StandardOutput=journal
StandardError=journal
```

**2. 创建 timer 文件**

```bash
sudo vim /etc/systemd/system/lof-hacker.timer
```

```ini
[Unit]
Description=Run LOF Hacker daily at 10:00 and 13:00
Requires=lof-hacker.service

[Timer]
# 每天 10:00 和 13:00 各触发一次（使用多行 OnCalendar）
OnCalendar=*-*-* 10:00:00
OnCalendar=*-*-* 13:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**注意**：
1. 修改成你自己的项目目录

**3. 启用并启动 timer**

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用 timer
sudo systemctl enable lof-hacker.timer
sudo systemctl start lof-hacker.timer

# 查看状态
sudo systemctl list-timers
sudo systemctl status lof-hacker.timer
```

---

## 7. 步骤 6：验证和监控

### 7.1 验证 systemd timer

```bash
# 查看所有激活的 timer
systemctl list-timers

# 查看 lof-hacker timer 状态
systemctl status lof-hacker.timer

# 查看 timer 详细信息（包括下次触发时间）
systemctl list-timers lof-hacker.timer --all
```

### 7.2 查看 systemd journal 日志

```bash
# 查看服务的所有日志
journalctl -u lof-hacker.service

# 实时跟踪日志
journalctl -fu lof-hacker.service

# 查看今天的日志
journalctl -u lof-hacker.service --since today

# 查看最近 100 行日志
journalctl -u lof-hacker.service -n 100

# 搜索特定内容
journalctl -u lof-hacker.service | grep "arbitrage"
journalctl -u lof-hacker.service | grep "ERROR"
```

### 7.3 查看应用日志

```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看最近的日志
tail -100 logs/app.log

# 搜索特定内容
grep "ERROR" logs/app.log
grep "arbitrage opportunities" logs/app.log
```

### 7.4 手动触发测试

```bash
# 手动运行一次
cd /path-to-your-project/LOF-HACKER-JISILU
source .venv/bin/activate
python main.py

# 或者直接使用 venv 中的 python
/root/LOF-HACKER-JISILU/.venv/bin/python /root/LOF-HACKER-JISILU/main.py
```

---

## 8. 常见问题

### 8.1 Cookie 过期

**症状**：日志显示"Login failed"或"cookies expired"

**解决方案**：
```bash
# 1. 在浏览器重新登录并导出 Cookie
# 2. 上传新的 Cookie 文件
scp data/.jisilu_cookies.json root@your-server-ip:/root/LOF-HACKER-JISILU/data/

# 3. 或者使用加密凭证自动登录（无需 Cookie）
vim .env
# 填写 JISILU_ENCRYPTED_USERNAME 和 JISILU_ENCRYPTED_PASSWORD
```

### 8.2 邮件发送失败

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

### 8.3 定时任务未执行

**检查步骤**：
```bash
# 1. 确认 cron 服务运行中
sudo systemctl status cron

# 2. 查看 crontab 配置
crontab -l

# 3. 检查 cron 日志
sudo tail -f /var/log/cron

# 4. 检查脚本路径是否正确
which python
ls -la /root/LOF-HACKER-JISILU/.venv/bin/python
```

### 8.4 权限问题

**症状**：日志显示"Permission denied"

**解决方案**：
```bash
# 修复目录权限
chmod -R 755 /root/LOF-HACKER-JISILU
chmod 644 /root/LOF-HACKER-JISILU/.env
chmod 644 /root/LOF-HACKER-JISILU/logs/app.log

# 确保虚拟环境可执行
chmod +x /root/LOF-HACKER-JISILU/.venv/bin/python
```

### 8.5 内存不足

**症状**：进程被系统杀死

**解决方案**：
```bash
# 1. 增加 swap 空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. 验证 swap
free -h

# 3. 永久生效（添加到 fstab）
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 附录 A：完整部署命令清单

```bash
# ===== 1. 安装 Python 环境 =====
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# ===== 2. 克隆代码 =====
cd /root
git clone https://github.com/your-username/LOF-HACKER-JISILU.git
cd LOF-HACKER-JISILU

# ===== 3. 创建虚拟环境 =====
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ===== 4. 配置应用 =====
cp .env.example .env
vim .env  # 填写配置

# ===== 5. 创建日志目录 =====
mkdir -p logs
touch logs/app.log

# ===== 6. 测试运行 =====
python main.py

# ===== 7. 设置定时任务 =====
crontab -e
# 添加：0 13 * * * cd /root/LOF-HACKER-JISILU && /root/LOF-HACKER-JISILU/.venv/bin/python /root/LOF-HACKER-JISILU/main.py >> /root/LOF-HACKER-JISILU/logs/cron.log 2>&1

# ===== 8. 验证 =====
crontab -l
tail -f logs/app.log
```

---

## 附录 B：成本估算

| 项目 | 配置         | 价格（月） |
|------|------------|-----------|
| ECS 实例 | 2 核 2G     | ¥60-80 |
| 带宽 | 按量付费 3Mbps | ¥20-30 |
| 系统盘 | 40GB 高效云盘  | ¥10 |
| **总计** |            | **¥90-120/月** |

> 注：价格仅供参考，实际价格以阿里云官网为准。新用户通常有优惠活动。

---

## 附录 C：安全建议

1. **使用 SSH 密钥登录**
   ```bash
   # 生成密钥对
   ssh-keygen -t ed25519
   
   # 上传公钥到服务器
   ssh-copy-id root@your-server-ip
   
   # 禁用密码登录（可选）
   sudo vim /etc/ssh/sshd_config
   # PasswordAuthentication no
   ```

2. **配置防火墙**
   ```bash
   # 安装 ufw（Ubuntu）
   sudo apt install ufw
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **监控资源使用**
   ```bash
   # 安装 htop
   sudo apt install htop
   
   # 查看资源使用
   htop
   ```

---

## 联系支持

如有问题，请查看：
- [README.md](../README.md) - 项目说明
- [COOKIE_SETUP.md](COOKIE_SETUP.md) - Cookie 设置指南
- [FEISHU_SETUP.md](FEISHU_SETUP.md) - 飞书通知设置
