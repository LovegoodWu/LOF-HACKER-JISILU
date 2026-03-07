# 飞书通知配置指南

本指南介绍如何配置 LOF Hacker 的飞书通知功能。

## 一、什么是飞书机器人

飞书机器人是飞书群聊中的自动化助手，可以通过 Webhook API 向群聊发送消息。LOF Hacker 使用飞书机器人推送 LOF 套利机会提醒。

## 二、创建飞书机器人

### 步骤 1：打开飞书群聊

在飞书中选择一个群聊（或创建新群），用于接收 LOF 套利提醒。

### 步骤 2：添加自定义机器人

1. 点击群聊右上角的 **设置** 图标（⚙️）
2. 找到并点击 **机器人** 选项
3. 点击 **添加机器人**
4. 选择 **自定义机器人**

### 步骤 3：配置机器人

1. **机器人名称**：输入名称，如 "LOF Hacker"
2. **头像**：可选
3. **安全设置**（三选一）：
   - **自定义关键词**（推荐）：添加关键词 "LOF" 或 "套利"
   - **加签**：需要额外的签名配置
   - **IP 地址**：需要配置服务器 IP

4. 点击 **完成**

### 步骤 4：复制 Webhook URL

机器人创建成功后，会显示一个 Webhook URL，格式如下：

```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**请复制并保存此 URL**

## 三、配置 LOF Hacker

### 步骤 1：编辑 .env 文件

在项目根目录打开 `.env` 文件（如果没有，复制 `.env.example` 为 `.env`）

### 步骤 2：填入飞书配置

```ini
# 启用飞书通知
FEISHU_ENABLED=true

# 填入你复制的 Webhook URL
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的 webhook 地址

# 消息类型（可选）
# interactive = 交互式卡片消息（推荐，格式美观）
# text = 纯文本消息
FEISHU_MESSAGE_TYPE=interactive
```

### 步骤 3：保存文件

## 四、测试飞书通知

### 方法一：使用测试脚本

```bash
# 在项目根目录或 docs 目录下均可执行
python ../tools/test_feishu.py
```

### 方法二：使用主程序测试

```bash
# 在项目根目录或 docs 目录下均可执行
python ../main.py --test
```

如果配置正确，你会在飞书群聊中收到一条测试消息。

## 五、消息格式示例

### 交互式卡片消息（推荐）

```
┌─────────────────────────────────────┐
│ LOF 套利机会提醒                    │
├─────────────────────────────────────┤
│ ⏰ 时间：2024-01-01 13:00:00        │
│ 📊 共发现 3 个套利机会              │
│ 筛选条件：溢价率 > 0.5%             │
│                                     │
│ 1. 161128 华宝油气                  │
│    溢价率：1.25% | 状态：限额       │
│                                     │
│ 2. 160123 南方原油                  │
│    溢价率：0.89% | 状态：限额       │
│                                     │
│ ...                                 │
└─────────────────────────────────────┘
```

### 纯文本消息

```
【LOF 套利机会提醒】

⏰ 时间：2024-01-01 13:00:00
📊 共发现 3 个套利机会
筛选条件：溢价率 > 0.5%

1. 161128 华宝油气
   溢价率：1.25% | 状态：限额

2. 160123 南方原油
   溢价率：0.89% | 状态：限额

... 还有 1 个机会，请查看完整列表
```

## 六、常见问题

### Q1: 消息发送失败？

**检查清单：**
- [ ] FEISHU_ENABLED 是否设置为 `true`
- [ ] FEISHU_WEBHOOK_URL 是否正确复制
- [ ] 机器人是否已添加到群聊
- [ ] 安全设置中的关键词是否包含 "LOF" 或 "套利"

### Q2: 如何同时使用邮件和飞书通知？

可以同时配置两种方式，LOF Hacker 会同时发送：

```ini
# 邮件配置
EMAIL_USERNAME=your_email@126.com
EMAIL_PASSWORD=your_auth_code
EMAIL_RECIPIENT=recipient@example.com

# 飞书配置
FEISHU_ENABLED=true
FEISHU_WEBHOOK_URL=https://...
```

### Q3: 如何关闭飞书通知？

将 `FEISHU_ENABLED` 设置为 `false`：

```ini
FEISHU_ENABLED=false
```

## 七、安全提示

1. **不要分享 Webhook URL**：任何人拿到这个 URL 都可以向你的群聊发送消息
2. **使用自定义关键词**：防止其他机器人误发消息到你的群聊
3. **定期检查机器人状态**：确保机器人仍在群聊中

## 八、相关文档

- [LOF Hacker 使用文档](README.md)
- [安全托管指南](docs/SECURITY.md)
- [飞书开放平台文档](https://open.feishu.cn/document/ukTMzUjL4YDM00i2NATN)
