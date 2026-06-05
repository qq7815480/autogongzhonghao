# 正文配图失败后的修复流程

触发：用户反馈公众号草稿「正文配图失败」「正文图都没了」「图片不显示」。本流程适用于文章已经进草稿箱，但正文图片缺失或未正确上传的情况。

## 先判断原因

1. 检查文章目录是否存在正文图：`sunwork/<date-slug>/images/` 或 `imgs/`。
2. 检查 `article.md` 是否有 Markdown 图片引用：`![描述](...)`。
3. 常见原因：
   - `publish.py` 发布时文章中没有图片引用，因此输出「文章中没有找到图片引用」。
   - 图片引用是相对路径（如 `images/01.png`），脚本在 `scripts/` 目录运行时解析失败。
   - 分步发布时上传了图片，但没有在转 HTML 前把本地路径替换为微信 CDN URL。

## 快速修复步骤

1. 生成或补齐正文图：
   - 写 prompt 到 `prompts/NN-*.md` 作为复现记录。
   - 用 `image_generate` 生成图，复制到 `images/NN-*.png`。
   - 图中文字必须中文；每张图用 `vision_analyze` 快速检查乱码、裁切、可读性。

2. 在 `article.md` 插入图片引用：
   - 推荐使用本地**绝对路径**：
     `![描述](/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images/01-xxx.png)`
   - 不要只写 `images/01-xxx.png`。

3. 重跑 AI 味检测：
   ```bash
   cd ~/.hermes/skills/wechat-publisher/scripts
   python3 ai_score.py /path/to/article.md --threshold 45
   ```

4. 用分步发布创建新草稿（比整条 `publish.py` 更利于确认图片）：
   ```python
   import sys, re
   from pathlib import Path
   sys.path.insert(0, '/Users/sun/.hermes/skills/wechat-publisher/scripts')
   from api import set_account, upload_thumb_image, upload_content_image, add_draft
   from html_converter import convert_markdown_to_wechat_html, load_theme
   from config import get_config

   base = Path('/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>')
   article_path = base / 'article.md'
   cover_path = base / 'cover.png'
   imgs_dir = base / 'images'

   set_account('main')
   config = get_config('main')

   cover_id = upload_thumb_image(cover_path)

   image_urls = {}
   for p in sorted(imgs_dir.glob('*.png')):
       url = upload_content_image(p)
       if not url.startswith('http'):
           m = re.search(r'https?://\S+', url)
           url = m.group(0) if m else url
       image_urls[str(p)] = url

   md = article_path.read_text(encoding='utf-8')
   for local, url in image_urls.items():
       md = md.replace(local, url)

   # Verify all Markdown image refs are CDN URLs before conversion.
   refs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md)
   assert refs and all(r.startswith('https://mmbiz.qpic.cn/') for r in refs), refs

   styles, highlights, divider, list_style = load_theme('warm-editorial')
   html = convert_markdown_to_wechat_html(
       md,
       styles=styles,
       highlights=highlights,
       divider_text=divider,
       list_style=list_style,
   )
   (base / 'article_with_images.html').write_text(html, encoding='utf-8')

   media_id = add_draft({
       'title': '短标题',
       'author': config.get('author', '豌豆四喜'),
       'digest': '120字以内摘要',
       'content': html,
       'thumb_media_id': cover_id,
       'need_open_comment': 1,
       'only_fans_can_comment': 0,
   })
   print('new_draft_media_id=', media_id)
   ```

## 用户沟通

- 明确告诉用户「旧草稿可以删，看最新草稿」。
- 只汇报关键状态：配图张数、上传状态、AI 味分、草稿标题/账号。
- 不要解释一大堆内部失败细节，除非用户追问。

## 本次验证过的要点

- 对已进草稿但正文无图的情况，重新补图并新建草稿比尝试原地更新更稳。
- 上传正文图后，必须在调用 `convert_markdown_to_wechat_html` 前完成本地路径 → 微信 CDN URL 替换。
- HTML 转换前可用正则检查所有 `![](...)` 都是 `https://mmbiz.qpic.cn/`，避免再次发布无效图片。
