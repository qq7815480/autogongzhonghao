# 微信草稿缺图后的原地修复与回读验收

适用场景：正文图片未全部上传，但草稿已经创建；已知该草稿的精确 `media_id`，且希望避免删除、重建和同标题重复草稿。

## 核心原则

- 图片上传必须串行完成并严格达到 `N/N`，再更新草稿。
- 优先使用微信 `draft/update` 原地覆盖已知草稿；不要先删除，也不要新建同标题草稿。
- 更新成功不能只看 `errcode: 0`，必须再调用 `draft/get` 回读标题和正文图片数。
- 所有 JSON 请求必须使用 `json.dumps(..., ensure_ascii=False).encode('utf-8')`，严禁 `requests.post(json=payload)`。

## 修复流程

1. 从 `article.md` 提取全部本地正文图，确认均为绝对路径和合法 PNG/JPEG。
2. 使用 `api.upload_content_image()` 逐张串行上传，保存本地路径到微信 CDN URL 的映射。
3. 断言上传结果数等于正文图片总数；任意失败立即停止，不生成 HTML，不更新草稿。
4. 在 Markdown 中将全部本地路径替换为 CDN URL。
5. 用 `warm-editorial` 主题转换 HTML，并断言 HTML 中 `https://mmbiz.qpic.cn/` 的数量等于正文图数量。
6. 调用：

```python
payload = {
    'media_id': exact_media_id,
    'index': 0,
    'articles': article_dict,
}
requests.post(
    f'{API_BASE}/draft/update?access_token={token}',
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'},
    timeout=60,
)
```

7. 更新返回 `errcode == 0` 后，用 `draft/get` 回读同一个精确 `media_id`。
8. 微信响应头可能缺少正确 charset，`requests.Response.json()` 或 `.text` 可能把中文显示成 mojibake。验收时显式使用：

```python
got = json.loads(response.content.decode('utf-8'))
```

9. 最终断言：标题逐字正确、作者与摘要正确、正文 CDN 图片数量严格为 `N`。

## 发布脚本的实现级硬门槛

`process_article_images()` 返回后、HTML 转换和草稿创建前，必须比较发现数与成功映射数：

```python
discovered = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content_md)
if len(img_mapping) != len(discovered):
    raise RuntimeError(
        f'正文图片上传不完整：{len(img_mapping)}/{len(discovered)}，停止创建草稿'
    )
```

不能因为后续草稿 API 成功，就把缺图草稿报告为成功。
