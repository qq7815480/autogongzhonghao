# GitHub 文档维护与凭证脱敏

## 推送到 GitHub 的流程

### 1. 检查敏感信息

提交前必须扫描所有 staged 文件，确保没有真实凭证：

```bash
cd ~/.hermes/skills/wechat-publisher
git add -A
git diff --cached --name-only | xargs grep -l "app_secret\|<real_app_id>\|<any_real_secret>" 2>/dev/null
```

**必须脱敏的字段：**
- `app_id` — 微信公众号 AppID
- `app_secret` — 微信公众号 AppSecret
- 任何 API Key、Token、密码
- IP 地址（如果是内网/特定服务器）

**安全的占位符：**
```yaml
app_id: "wx1234567890abcdef"
app_secret: "your_app_secret_here"
```

### 2. .gitignore 确认

确保以下文件/目录在 `.gitignore` 中：
- `wechat-publisher.yaml`（真实配置）
- `sunwork/`（工作产出，含文章草稿和图片）
- `scripts/.token_cache*`（access_token 缓存）

### 3. 提交并推送

```bash
git commit -m "docs: 描述性提交信息"
git push origin main
```

### 4. GitHub 认证

如果 `git push` 失败（`could not read Username`），需要配置认证：

**方案 A：Personal Access Token**
1. https://github.com/settings/tokens → Generate new token (classic)
2. 勾选 `repo` 权限
3. `git config --global credential.helper store`
4. `git remote set-url origin https://<username>:<token>@github.com/jiji262/wechat-publisher.git`

**方案 B：SSH Key**
```bash
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
# 添加到 https://github.com/settings/keys
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**方案 C：cua-driver 操控浏览器登录**
安装 cua-driver 后可用 `computer_use` 工具操控 Chrome 浏览器完成 GitHub OAuth 登录。
需要 macOS Accessibility + Screen Recording 权限。详见 `macos-computer-use` skill。

## 常见坑

- `wechat-publisher.yaml` 已在 `.gitignore` 中，不会被提交。但如果之前误提交过，需要 `git rm --cached` 移除
- `sunwork/` 目录包含实际文章草稿，不要提交到公开仓库
- SKILL.md 中的示例凭证（如 `wx1234567890abcdef`）是安全的占位符，可以提交
