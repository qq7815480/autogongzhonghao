# 微信 CDN 图片防盗链解决方案

## 问题

微信公众号文章中的图片托管在 `mmbiz.qpic.cn` / `mmbiz.qlogo.cn`，有防盗链机制。直接用 `requests.get()` 下载时：
- 可能返回 HTML 错误页（Content-Type 仍可能是 image/*）
- 上传到微信 API 时报 `40137: invalid image format`

## 根因

`download_image()` 原实现只设了 `User-Agent`，没设 `Referer`。微信 CDN 检查 Referer 来源。

## 解决方案（已实装于 `scripts/image_handler.py`）

### 1. 自动添加 Referer
检测 URL 域名是否为微信 CDN，自动注入 `Referer: https://mp.weixin.qq.com/`。

### 2. Magic bytes 验证（`_is_valid_image()`）
下载后检查文件头 16 字节：
| 格式 | Magic bytes |
|---|---|
| JPEG | `FF D8 FF` |
| PNG | `89 50 4E 47` |
| GIF | `47 49 46 38` |
| WebP | `RIFF....WEBP` |
| BMP | `42 4D` |

不匹配任何已知格式 → 判定为防盗链错误页，删除文件，触发备用方案。

### 3. Curl 备用下载（`_download_with_crawl4ai()`）
requests 失败后，用 curl 带完整浏览器 headers 重试：
- `Referer: https://mp.weixin.qq.com/`
- `Sec-Fetch-Dest: image` / `Sec-Fetch-Mode: no-cors` / `Sec-Fetch-Site: cross-site`
- `sec-ch-ua` / `sec-ch-ua-mobile` / `sec-ch-ua-platform`

模拟 Chrome 看图请求，绕过更严格的防盗链检查。

## 测试验证（2026-05-07）
- 真实微信图片 URL `mmbiz.qpic.cn/sz_mmbiz_jpg/...` 下载成功（97KB，JPEG）
- HTML 错误页被 `_is_valid_image()` 正确拦截（返回 False）

## 注意事项
- 并非所有微信图片都有防盗链，部分 URL 不带 Referer 也能下载
- 备用方案依赖系统 curl，macOS/Linux 自带
- 如果 curl 也失败（极少见），说明图片 URL 已过期或被删除，需用户手动处理
