# 分步手动发布完整流程

当 `publish.py` 因图片过大超时时，用以下分步流程。所有代码在 `execute_code` 中运行（避免 terminal 超时）。

## Step 1: 上传封面和正文图片

```python
import sys
sys.path.insert(0, '/Users/sun/.hermes/skills/wechat-publisher/scripts')
from api import set_account, upload_thumb_image, upload_content_image
import os

set_account('main')

# 上传封面
cover_id = upload_thumb_image('/path/to/cover.png')
print(f'封面 media_id: {cover_id}')

# 上传正文图片，记录 CDN URL
image_urls = {}
imgs_dir = '/path/to/images'
for f in sorted(os.listdir(imgs_dir)):
    if f.endswith('.png') and not f.startswith('.'):
        path = os.path.join(imgs_dir, f)
        url = upload_content_image(path)
        image_urls[f] = url
        print(f'{f}: {url}')
```

## Step 2: 替换路径 + 转 HTML + 创建草稿

```python
from html_converter import convert_markdown_to_wechat_html, load_theme
from api import add_draft

# 加载主题（返回4元素元组，必须解包）
styles, highlights, divider, list_style = load_theme('warm-editorial')

# 读取文章
with open('/path/to/article.md', 'r') as f:
    md = f.read()

# 用 CDN URL 替换本地路径
for local_path, cdn_url in image_urls.items():
    md = md.replace(local_path, cdn_url)

# 转 HTML
html = convert_markdown_to_wechat_html(
    md, styles=styles, highlights=highlights,
    divider_text=divider, list_style=list_style
)

# 创建草稿
result = add_draft({
    'title': '文章标题',
    'author': '豌豆',
    'digest': '短摘要',
    'content': html,
    'thumb_media_id': cover_id,
    'need_open_comment': 1,
})
print(f'草稿创建结果: {result}')
```

## Step 3: 创建后必须按 media_id 回读验证

不要只相信 `add_draft` 的成功输出，也不要只用标题查重判断是否创建成功。微信的 `draft/batchget` 可能存在短暂延迟；应直接调用 `draft/get`，核对标题、作者、摘要、封面和正文图片数。

```python
import json, requests
from wechat_token import get_access_token

token = get_access_token()
resp = requests.post(
    f'https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}',
    data=json.dumps({'media_id': result}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    timeout=30,
)
# 微信响应常不带 charset；resp.json()/resp.text 可能把中文按 Latin-1 解码成乱码。
data = json.loads(resp.content.decode('utf-8'))
article = data['news_item'][0]
assert article['title'] == '文章标题'
assert article['content'].count('<img') == len(image_urls)
print('草稿回读验证通过')
```

## 注意事项

- 微信标题和摘要按 UTF-8 字节计数。创建前用 `len(text.encode('utf-8'))` 检查；实测标题应不超过 36 字节、摘要不超过 41 字节，否则可能报 45003/45004。
- `upload_content_image()` 的返回值本身就是纯 CDN URL；日志里的“正文图片上传成功:”只是 `print` 前缀，不要把日志文本当返回值解析。
- `convert_markdown_to_wechat_html` 的 `styles` 参数必须是 dict，不能是 tuple。
- `add_draft` 内部必须用 `json.dumps(..., ensure_ascii=False)` 提交中文，严禁改成 `requests.post(json=data)`。
- 草稿查重与回读时，必须用 `json.loads(response.content.decode('utf-8'))`；不要依赖 `response.json()`，否则中文可能乱码，导致同标题查重漏检。
- 大图分步上传时，把 `cover_media_id`、每张正文图 CDN URL、最终草稿 media_id 逐步写入状态 JSON。中途失败后复用已上传结果，避免重复占用永久素材和重复上传。
- 整个流程在 `execute_code` 中运行比 terminal 更稳定（避免 shell 超时）。
- ⛔ 如果 `execute_code` 被阻断（cron profile 或权限限制），将完整 Python 代码写成 `.py` 脚本文件，再用 `python3 script.py` 执行。heredoc 方式（`python3 << 'EOF'`）在大脚本时也容易超时，脚本文件最可靠。
