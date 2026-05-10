# wechat-publisher 安装踩坑记录

## 环境: macOS ARM64, 系统 Python 3.9

### 依赖安装

系统 Python (CommandLineTools) 不支持 `--break-system-packages`:

```bash
# ❌ 会报错
python3 -m pip install requests pyyaml --break-system-packages

# ✅ 正确写法
python3 -m pip install requests pyyaml
```

urllib3 会报警告 (LibreSSL 2.8.3 < OpenSSL 1.1.1+)，可忽略。

### 生图方案: 跳过 bun/TypeScript

`generate_image.py` 内部调用 `bun scripts/baoyu_image_gen.ts`，macOS 默认无 bun。
解决方案: 跳过 `generate_image.py`，直接用 Hermes 内置 `image_generate` 工具 (GPT Image 2 via openai-codex)。

### API 验证

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 -c "from wechat_api import get_access_token; print('OK:', get_access_token()[:10]+'...')"
```

成功输出: `OK: 103_60ywkI...`
`40164` 错误 = IP 未加白名单，用 `curl -s https://api.ipify.org` 获取公网 IP。

### image_handler.py 上传输出格式

上传成功后输出包含中文前缀:
```
正文图片上传成功: https://mmbiz.qpic.cn/...
```

解析时需用正则提取 URL:
```python
import re
match = re.search(r'(https://mmbiz\.qpic\.cn/[^\s"]+)', output)
```

JSON 输出也有同样前缀，`json.loads()` 会失败，需先 strip。

### publish.py 图片处理流程

`publish.py` 会自动重新下载 CDN URL 图片并重新上传 (安全机制)。
所以阶段四手动上传的图片会被 publish.py 重新处理一次——这是正常的，不需要阻止。

### 当前配置

- 账号: `main` (sunwork)
- 主题: `warm-editorial` (暖色杂志风，栗色+米白+宋体)
- 封面风格: 文艺手绘 (scene+earth+hand-drawn+subtle，通过 baoyu-cover-image)
- 生图: GPT Image 2 (openai-codex provider)
- IP 白名单: `64.118.158.198`
