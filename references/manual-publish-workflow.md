# 手动发布流程 (publish.py 超时时的备选方案)

当 `publish.py` 因大图片超时时，分步执行以下流程。

## 步骤

### 1. 上传封面图

```python
from api import set_account, upload_thumb_image
set_account('main')
thumb_media_id = upload_thumb_image('/path/to/cover.jpg')
# 返回: media_id=xxx
```

### 2. 逐张上传正文图片

```python
from api import upload_content_image
raw_output = upload_content_image('/path/to/images/01.png')
```

⚠️ `upload_content_image()` 输出有中文前缀 `正文图片上传成功: `，直接 `json.loads()` 会失败。必须用正则提取 CDN URL：
```python
import re
match = re.search(r'https://mmbiz\.qpic\.cn[^\s"]+', raw_output)
cdn_url = match.group(0) if match else None
```

### 3. 替换文章中的图片路径

读取 `article.md`，将所有 `images/XX.png` 替换为对应的微信 CDN URL。

### 4. 转换 HTML

```bash
python3 html_converter.py article.md --theme warm-editorial -o article.html
```

或 Python 中：
```python
from html_converter import convert_md_to_html
html = convert_md_to_html(content, theme='warm-editorial')
```

### 5. 创建草稿

**⛔ 严禁用 `requests.post(url, json=data)`** — 默认 `ensure_ascii=True`，中文会变成 `\uXXXX` 转义序列，微信解析后全部乱码。

**正确方式**: 用 `api.add_draft()`（内部 `ensure_ascii=False` + `encode('utf-8')`）:
```python
from api import set_account, add_draft
set_account('main')
media_id = add_draft({
    'title': '标题(≤36字节)',
    'author': '老孙',
    'digest': '摘要(≤41字节)',
    'content': html,
    'thumb_media_id': thumb_media_id,
    'need_open_comment': 1,
    'only_fans_can_comment': 0,
})
```

如果必须直接调 requests:
```python
resp = requests.post(url,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={"Content-Type": "application/json; charset=utf-8"})
```

### 6. 发布前检查重复草稿

创建草稿前，先用 `draft/batchget` 检查是否已有同标题草稿，避免重复：
```python
url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}'
resp = requests.post(url, json={'offset': 0, 'count': 20, 'no_content': 1}, timeout=30)
# 检查返回的 item 列表中是否已有同标题草稿
```

## API 限制

- 标题: ≤36 字节 UTF-8 (约12个中文字符)，超限报 45003
- 摘要(digest): ≤41 字节 UTF-8，超限报 45004
- 内容 HTML: 无明确大小限制，但超大内容可能导致超时
- 封面图 thumb_media_id: 必须先通过 `upload_thumb_image` 上传
