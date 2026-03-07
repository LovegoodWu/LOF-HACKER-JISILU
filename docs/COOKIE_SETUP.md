# Cookie 设置指南

## 概述

本项目使用 **Cookie 文件** 方式进行集思录网站认证。这是唯一推荐的认证方式。

## 为什么使用 Cookie 文件？

集思录网站需要多个 cookie 才能正常登录，包括：
- `kbzw__Session` - 会话 ID
- `kbzw__user_login` - 登录凭证（关键！）
- `HMACCOUNT` - 计数器
- `kbz_newcookie` - 新 cookie 标记
- 其他统计 cookie

单独设置 `JISILU_SESSION` 是无效的，因为缺少其他必要的 cookie。

## 获取 Cookie 文件

### 步骤 1：登录集思录

1. 打开浏览器（Chrome/Edge/Firefox）
2. 访问 https://www.jisilu.cn/
3. 使用您的账号密码登录
4. 确保登录成功，可以看到您的用户名

### 步骤 2：导出 Cookies

#### 方法一：使用浏览器 Console（推荐）

这是最简单的方法，适用于所有现代浏览器：

1. 按 `F12` 打开开发者工具
2. 切换到 **Console** 标签
3. 复制并执行以下命令：

```javascript
copy(JSON.stringify(document.cookie.split('; ').map(c => {
    const [name, value] = c.split('=');
    return {name, value, domain: '.jisilu.cn', path: '/'};
}), null, 2));
```

4. 命令会自动将格式化的 JSON 复制到剪贴板

### 步骤 3：保存 Cookie 文件

1. 在项目根目录创建文件 `.jisilu_cookies.json`
2. 将复制的 JSON 内容粘贴到文件中
3. 保存文件

文件格式示例：
```json
[
  {
    "name": "kbzw__Session",
    "value": "your_session_id_here",
    "domain": ".jisilu.cn",
    "path": "/"
  },
  {
    "name": "kbzw__user_login",
    "value": "your_login_token_here",
    "domain": ".jisilu.cn",
    "path": "/"
  },
  {
    "name": "HMACCOUNT",
    "value": "your_count_value_here",
    "domain": ".jisilu.cn",
    "path": "/"
  },
  ...
]
```

**注意**：示例中的 value 仅为占位符，实际导出的 cookie 值会是不同的字符串。

## 使用保存的 Cookies

一旦 cookie 文件存在，脚本会自动加载并使用它，无需重复登录。

## Cookie 过期处理

### 自动登录功能

当保存的 cookie 过期时，系统会：

1. **自动检测过期**：通过访问 API 验证 cookie 是否有效
2. **自动尝试登录**：使用配置的 `JISILU_USERNAME` 和 `JISILU_PASSWORD` 进行登录
3. **自动保存新 Cookie**：登录成功后，新 cookie 会自动保存到 `.jisilu_cookies.json`

**注意**：密码登录可能会遇到 rate limit（登录过于频繁），如果遇到此问题，请等待 1 分钟后重试，或直接从浏览器导出新的 cookie。

### 手动刷新 Cookie

如果自动登录失败（例如密码登录被限制），可以手动刷新：

1. 按"步骤 2"重新从浏览器导出 cookies
2. 覆盖 `.jisilu_cookies.json` 文件
3. 重新运行脚本

## 清除 Cookies

如果需要重新登录（例如 cookies 过期），可以删除 cookie 文件：

```bash
rm .jisilu_cookies.json
```

## 注意事项

1. **Cookie 有效期**：cookies 有有效期，过期后需要重新导出
2. **安全性**：不要分享您的 cookie 文件，它包含登录凭证
3. **浏览器绑定**：cookies 与特定浏览器和设备绑定
4. **唯一认证方式**：Cookie 文件是唯一的认证方式，请确保正确配置

## 故障排除

### 问题：无法获取数据

1. 检查 cookie 文件是否存在于项目根目录
2. 检查 cookie 文件格式是否正确（JSON 数组）
3. 尝试重新导出 cookies（可能已过期）

### 问题：提示未登录

1. 确认已登录集思录网站
2. 确认导出的是完整的 cookies（至少 6 个）
3. 确认 cookie 文件包含 `kbzw__user_login`
