# 公众号正文配图失败后的重传检查清单

适用场景：公众号草稿已创建，但用户反馈正文配图失败、后台看不到图、或文章源文件里没有图片引用。

## 原则

- 不要只重新上传封面；正文图必须先进入 Markdown，再转 HTML，再创建新草稿。
- 正文图片必须使用微信 `uploadimg` 返回的 `mmbiz.qpic.cn` CDN URL，不能把本地路径留在 HTML 里。
- 创建草稿前必须做一次断言：Markdown/HTML 中存在正文图片 CDN 引用，且没有剩余本地图片路径。

## 推荐流程

1. 检查文章源文件是否有 `![...](...)` 图片引用。
2. 若没有正文图：
   - 生成或整理正文图到 `{workdir}/images/`；
   - 在对应小节后插入 `![alt](/absolute/path/to/images/xx.png)`；
   - 每张图先做视觉检查，确认无乱码、无严重裁切、适合发布。
3. 上传封面：`upload_thumb_image(cover.png)`。
4. 上传正文图：遍历 `images/*.png` 调 `upload_content_image(path)`。
5. 用返回的纯 URL 替换 Markdown 中的本地绝对路径。
6. 转 HTML 前检查：
   - `正文微信图片数 >= 1`；
   - 所有图片引用都以 `https://mmbiz.qpic.cn` 或 `https://mmbiz.qpic.cn/sz_mmbiz_` 开头。
7. 转 HTML 后再次检查 HTML 中包含 `mmbiz.qpic.cn`。
8. 创建新草稿，并告诉用户看“最新生成的那篇”，旧草稿可删。

## 最小断言代码片段

```python
import re, json

remaining = [x for x in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md)
             if not x.startswith('https://mmbiz.qpic.cn')]
if remaining:
    raise RuntimeError('仍有非微信CDN图片引用: ' + json.dumps(remaining, ensure_ascii=False))

wechat_imgs = re.findall(r'!\[[^\]]*\]\((https://mmbiz\.qpic\.cn[^)]+)\)', md)
print('正文微信图片数:', len(wechat_imgs))
if not wechat_imgs:
    raise RuntimeError('Markdown 中没有正文微信图片 CDN 引用')

html = convert_markdown_to_wechat_html(...)
if 'mmbiz.qpic.cn' not in html:
    raise RuntimeError('HTML中没有微信图片CDN引用')
```

## 用户沟通

- 用户说“正文里的配图都失败了”时，直接按上面流程修复并重新创建草稿；不要只解释原因。
- 回报用简表：账号、标题、封面、正文配图数量、草稿 media_id。
