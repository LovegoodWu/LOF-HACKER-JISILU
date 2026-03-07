# 集思录加密登录配置指南

本文档说明如何配置加密后的用户名和密码用于自动登录集思录。

## 背景

集思录网站在登录时对用户名和密码进行加密传输：
- **用户名**：使用 MD5 加密（32 位十六进制字符串）
- **密码**：使用 AES-256 加密（64 位十六进制字符串）

为了避免逆向工程加密算法，最简单的方法是直接从浏览器的登录请求中获取加密后的值。

## 配置步骤

### 步骤 1：登录集思录

1. 打开浏览器（推荐使用 Chrome 或 Edge）
2. 访问 https://www.jisilu.cn
3. 如果已登录，请先退出登录

### 步骤 2：打开开发者工具

1. 按 `F12` 打开开发者工具
2. 切换到 **Network**（网络）标签
3. 勾选 **Preserve log**（保留日志）选项

### 步骤 3：执行登录

1. 在登录页面输入你的用户名和密码
2. 点击登录按钮
3. 在 Network 标签中找到 `login_process` 请求（POST 请求）

### 步骤 4：获取加密值

1. 点击 `login_process` 请求
2. 切换到 **Payload** 或 **Request** 标签
3. 查看请求参数，你会看到：
   - `user_name`: 加密后的用户名（32 位字符串）
   - `password`: 加密后的密码（64 位字符串）
   - `aes`: "1"（表示密码已加密）

### 步骤 5：配置到 .env 文件

1. 复制 `user_name` 和 `password` 的值
2. 打开项目根目录的 `.env` 文件
3. 填入以下配置：

```bash
JISILU_ENCRYPTED_USERNAME=你的加密用户名（32 位）
JISILU_ENCRYPTED_PASSWORD=你的加密密码（64 位）
```

## 示例

```bash
# 加密后的用户名（MD5，32 位）
JISILU_ENCRYPTED_USERNAME=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# 加密后的密码（AES-256，64 位）
JISILU_ENCRYPTED_PASSWORD=q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6
```

## 验证配置

配置完成后，运行以下命令测试登录：

```bash
python main.py
```

查看日志输出，确认登录是否成功。

## 注意事项

1. **加密值会定期变化**：集思录可能会定期更换加密密钥，如果发现登录失败，请重新获取加密值
2. **Cookie 文件仍是推荐方式**：加密凭证登录是备用方案，Cookie 文件认证更稳定
3. **不要分享加密值**：加密后的用户名和密码等同于你的登录凭证，请勿泄露
4. **加密值格式**：
   - 用户名：32 位十六进制字符串（MD5）
   - 密码：64 位十六进制字符串（AES-256）

## 故障排除

### 登录失败：`Login failed: 用户名或密码错误`

- 加密值可能已过期，请重新从浏览器获取
- 检查 `.env` 文件中的值是否完整复制（无多余空格）

### 登录失败：`JISILU_ENCRYPTED_USERNAME or JISILU_ENCRYPTED_PASSWORD not configured`

- 确认 `.env` 文件已正确配置
- 确认 `.env` 文件在项目根目录

### 登录成功但无法获取数据

- 可能是 Cookie 文件缺失，登录成功后会自动保存 Cookie
- 检查网络连接是否正常

## 与 Cookie 文件认证的区别

| 特性 | Cookie 文件 | 加密凭证 |
|------|-----------|---------|
| 稳定性 | 高 | 中（加密值可能过期） |
| 配置复杂度 | 简单 | 简单 |
| 维护频率 | 需定期更新 | 需定期更新 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 相关文件

- [`config/settings.py`](../config/settings.py): 配置加载
- [`scraper/jisilu.py`](../scraper/jisilu.py): 登录实现
- [`.env.example`](../.env.example): 配置模板
