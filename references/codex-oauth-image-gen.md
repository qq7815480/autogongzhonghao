# Codex OAuth Token Management for GPT Image 2

## 概述

GPT Image 2 通过 `openai-codex` provider 使用，需要 Codex OAuth token（不是 API Key）。

## 认证流程

1. 终端运行 `codex` 命令
2. 选择 **ChatGPT 登录**（不是 API Key 模式）
3. 浏览器登录后，token 保存到 `~/.codex/auth.json`
4. 导入到 Hermes: `~/.hermes/auth.json` 的 `providers.openai-codex` 和 `credential_pool.openai-codex`

## Token 刷新

```python
import httpx

CODEX_OAUTH_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"  # 注意大小写
CODEX_OAUTH_TOKEN_URL = "https://auth.openai.com/oauth/token"

response = httpx.post(
    CODEX_OAUTH_TOKEN_URL,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CODEX_OAUTH_CLIENT_ID,
    },
    timeout=20.0,
)
# response.json() 包含新的 access_token 和 refresh_token
```

## 关键坑

- **两套存储**: `providers.openai-codex.tokens` 和 `credential_pool.openai-codex[0].access_token`。插件优先读 pool
- **refresh 后两处都要更新**: 否则 pool 里的旧 token 会导致 401 token_invalidated
- **client_id 大小写**: `app_EMoamEEZ73f0CkXaXp7hrann`（o 是小写）
- **Token 有效期**: ~10 天（239h），refresh_token 可续期
- **Cloudflare headers**: 插件自动添加 `originator: codex_cli_rs` 和 `ChatGPT-Account-ID`
- **Codex API 要求 streaming**: `stream: true` 和 `store: false`

## 验证

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/Users/sun/.hermes/hermes-agent')
from agent.auxiliary_client import _read_codex_access_token
token = _read_codex_access_token()
print('Token exists:', bool(token))
"
```
