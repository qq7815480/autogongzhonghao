# 微信正文图片上传完整性 Gate

适用场景：公众号文章含本地正文图，准备调用 `publish.py --input` 或手动分步发布前。

## 为什么需要

文件扩展名不代表真实格式。例如来源文件名为 `.png`，magic bytes 却是 RIFF/WebP；微信素材接口会返回 `40137 invalid image format`。旧发布流程可能在部分图片上传失败后仍继续创建草稿，最终得到缺图草稿。

## 发布前检查

1. 从 `article.md` 提取所有本地图片路径。
2. 用 `file` 或等价 magic-byte 检测确认真实格式。
3. 只允许微信正文图片接口支持且扩展名匹配的 JPEG/PNG/GIF。发现 WebP、AVIF、扩展名伪装或异常编码时，先转换成标准 JPEG/PNG，再更新 Markdown 路径。
4. 转换后用 `file` 和像素尺寸再次确认，并先单独调用 `upload_content_image()` 测试问题图片。

示例：

```bash
file /abs/path/image.png
sips -s format jpeg -s formatOptions 90 /abs/path/image.png --out /abs/path/image.jpg
file /abs/path/image.jpg
sips -g pixelWidth -g pixelHeight /abs/path/image.jpg
```

## 发布日志硬门槛

- 必须看到 `发现 N 张图片`。
- 必须看到 N 次正文图片上传成功。
- 成功计数必须严格为 `N/N`。
- 任意一张上传失败都应视为本次发布失败：停止 HTML 转换和草稿创建，先修图再重试。
- 不得把“草稿创建成功”当作整体成功；正文图上传完整性是独立验收项。
- **已知危险行为**：某些版本的 `publish.py` 在日志显示 `4/5` 等部分成功后仍会继续转换 HTML、上传封面并创建草稿。此时即使退出码为 0、输出 `status: success` 且返回草稿 `media_id`，也必须判定为发布失败。
- 遇到上述情况，把新草稿明确标记为“缺图无效草稿”，记录其精确 `media_id`，不要向用户报告任务完成，也不要自动群发。
- 恢复时先单独调用 `upload_content_image()` 重试失败图片；确认成功后，优先按分步发布流程重建，避免整批并发再次出现部分成功。
- 若同标题缺图草稿已经存在，先向用户说明并取得覆盖授权，然后只删除已记录的精确 `media_id`；严禁按标题关键词模糊删除。

## 已经创建了缺图草稿时

1. 记录缺图草稿的精确 `media_id`。
2. 修复并单独测试失败图片。
3. 按同标题查重规则处理：询问用户是否删除该精确草稿并重建，禁止模糊匹配删除。
4. 用户授权后，仅删除精确 `media_id`，再重新创建完整草稿。
5. 新日志必须满足 `N/N`，再向用户报告完成。

## 建议的实现级防线

`publish.py` 或图片处理层应在创建草稿前断言：

```python
if uploaded_count != discovered_count:
    raise RuntimeError(
        f"正文图片上传不完整：{uploaded_count}/{discovered_count}，停止创建草稿"
    )
```

不要把部分成功当作可继续状态。