# Git 安全托管指南

## ⚠️ 重要安全提示

本项目包含敏感信息（密码、API keys 等），请务必遵守以下安全规范：

## 1. 敏感文件列表

以下文件**绝对不能**提交到 Git：

| 文件 | 原因 | 状态 |
|------|------|------|
| `.env` | 包含密码、邮箱认证码等 | ✅ 已在 .gitignore 中 |
| `.jisilu_cookies.json` | 包含登录 Session | ✅ 已在 .gitignore 中 |
| `.jisilu_cookies.pkl` | 包含登录 Session | ✅ 已在 .gitignore 中 |
| `logs/*.log` | 可能包含敏感信息 | ✅ 已在 .gitignore 中 |

## 2. 首次设置步骤

```bash
# 1. 克隆仓库后，复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件，填入真实配置
vi .env  # 或使用其他编辑器

# 3. 确认 .env 文件不会被 Git 追踪
git status  # 应该看不到 .env 文件
```

## 3. 检查敏感文件

```bash
# 检查是否有敏感文件被追踪
git ls-files | grep -E '\.env$|cookies\.json$'

# 如果有输出，立即执行以下命令移除
git rm --cached .env
git rm --cached .jisilu_cookies.json
```

## 4. 如果已提交敏感信息

### 情况一：只在最近一次提交

```bash
# 撤销最近一次提交（保留更改）
git reset --soft HEAD~1

# 编辑移除敏感内容
# 然后重新提交
git add <安全文件>
git commit -m "your message"
```

### 情况二：已在历史提交中

使用 BFG Repo-Cleaner：

```bash
# 1. 下载 BFG: https://rtyley.github.io/bfg-repo-cleaner/

# 2. 清理敏感文件
bfg --delete-files .env
bfg --delete-files .jisilu_cookies.json

# 3. 清理 Git 历史
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制推送
git push --force
```

## 5. GitLab CI/CD 部署

如果使用 GitLab CI/CD 部署，使用 Variables 存储敏感配置：

### 设置步骤

1. 进入 GitLab 项目
2. Settings → CI/CD → Variables
3. 添加以下变量：

| Key | Value | Protected | Masked |
|-----|-------|-----------|--------|
| `DOTENV_CONTENT` | .env 文件完整内容 | ✅ | ✅ |
| `SSH_PRIVATE_KEY` | SSH 私钥（用于部署） | ✅ | ✅ |

### CI/CD 配置示例

```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  script:
    # 从变量创建 .env 文件
    - echo "$DOTENV_CONTENT" > .env
    # 执行部署
    - python main.py
```

## 6. 服务器部署

### 方式一：手动创建 .env

```bash
# 在服务器上
cd /path/to/LOFHacker
cp .env.example .env
vi .env  # 编辑真实配置

# 设置文件权限（仅所有者可读写）
chmod 600 .env
```

### 方式二：使用密钥管理服务

- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## 7. 安全检查清单

在提交代码前，请确认：

- [ ] `.env` 文件不存在于 `git status` 输出中
- [ ] `.jisilu_cookies.json` 不存在于 `git status` 输出中
- [ ] 没有密码、API key 等硬编码在代码中
- [ ] `.gitignore` 文件已正确配置
- [ ] 使用 `.env.example` 作为配置模板

## 8. 密码轮换

如果怀疑密码已泄露：

1. **立即修改**集思录密码
2. **立即修改**邮箱密码
3. **立即修改**飞书 webhook
4 撤销并重新生成所有 API keys

## 9. 联系

如有安全问题，请联系项目维护者。
